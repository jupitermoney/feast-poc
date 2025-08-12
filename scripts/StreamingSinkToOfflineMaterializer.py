import os
import json
import tempfile
import socket
import ssl
import boto3
from botocore.exceptions import ClientError
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from feast import FeatureStore
import pandas as pd
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('feast').setLevel(logging.DEBUG)

# --- Configuration ---
FEAST_REPO_PATH = "/Volumes/temp/feature_platform_testing/configs/feast/"

# --- Argument Parsing for Databricks Task Parameters ---
parser = argparse.ArgumentParser()
parser.add_argument('--topic', required=True, help='Kafka topic name')
parser.add_argument('--feature-view', required=True, help='Feature view name')
args = parser.parse_args()

TOPIC_NAME = args.topic
FEATURE_VIEW_NAME = args.feature_view

print(f"Received args: topic={TOPIC_NAME}, feature_view={FEATURE_VIEW_NAME}")

os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages=org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 pyspark-shell"

def get_secret_binary(secret_name, region_name="ap-south-1"):
    """Retrieve binary secret from AWS Secrets Manager"""
    boto3_session = boto3.Session(region_name=region_name)
    client = boto3_session.client(service_name='secretsmanager')
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        if 'SecretBinary' in get_secret_value_response:
            return get_secret_value_response['SecretBinary']
        elif 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString'].encode('utf-8')
        else:
            raise Exception("No secret binary or string found")
    except ClientError as e:
        raise Exception(f"Error retrieving secret: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")

def write_temp_file(content, suffix=".pem"):
    """Write content to a temporary file and return the path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='wb') as temp_file:
        if isinstance(content, str):
            content = content.encode('utf-8')
        temp_file.write(content)
        return temp_file.name

# Get all required secrets
try:
    cert_content = get_secret_binary("kafka-certificate.pem")
    cert_path = write_temp_file(cert_content, ".pem")
    key_content = get_secret_binary("kafka-key.pem")
    key_path = write_temp_file(key_content, ".pem")
    keystore_secret = json.loads(get_secret_binary("jm/kafka-keystore").decode('utf-8'))
    keystore_password = keystore_secret.get('password')
    kafka_brokers = "b-1.jm-dsprod-kafka-clust.85wcft.c2.kafka.ap-south-1.amazonaws.com:9094," + \
                    "b-2.jm-dsprod-kafka-clust.85wcft.c2.kafka.ap-south-1.amazonaws.com:9094," + \
                    "b-3.jm-dsprod-kafka-clust.85wcft.c2.kafka.ap-south-1.amazonaws.com:9094," + \
                    "b-4.jm-dsprod-kafka-clust.85wcft.c2.kafka.ap-south-1.amazonaws.com:9094"
    print("Successfully retrieved Kafka configuration and certificates")
except Exception as e:
    print(f"Error initializing Kafka configuration: {str(e)}")
    raise

# --- Spark Session Setup ---
spark = (
    SparkSession.builder
    .appName("feast-spark-online-store")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("INFO")

# --- Feast Store and Feature View ---
try:
    store = FeatureStore(repo_path=FEAST_REPO_PATH)
    print(f"Feast FeatureStore initialized from {FEAST_REPO_PATH}")
except Exception as e:
    print(f"Error initializing Feast FeatureStore: {e}")
    exit()

try:
    fv = store.get_feature_view(FEATURE_VIEW_NAME)
    print(f"Retrieved FeatureView: {fv.name}")
except Exception as e:
    print(f"Error retrieving FeatureView '{FEATURE_VIEW_NAME}': {e}")
    exit()

# --- Kafka SSL Options ---
kafka_ssl_options = {
    "kafka.bootstrap.servers": kafka_brokers,
    "kafka.security.protocol": "SSL",
    "kafka.ssl.ca.location": cert_path,
    "kafka.ssl.certificate.location": cert_path,
    "kafka.ssl.key.location": key_path,
    "kafka.ssl.key.password": keystore_password,
    "kafka.ssl.enabled.protocols": "TLSv1.2",
    "kafka.ssl.endpoint.identification.algorithm": "HTTPS"
}

# --- Get schema from feature view ---
schema_json = fv.stream_source.kafka_options.message_format.schema_json

# --- Read from Kafka as streaming DataFrame ---
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("kafka.security.protocol", "SSL") \
    .option("kafka.ssl.ca.location", cert_path) \
    .option("kafka.ssl.certificate.location", cert_path) \
    .option("kafka.ssl.key.location", key_path) \
    .option("kafka.ssl.key.password", keystore_password) \
    .option("kafka.ssl.enabled.protocols", "TLSv1.2") \
    .option("kafka.ssl.endpoint.identification.algorithm", "HTTPS") \
    .option("subscribe", TOPIC_NAME) \
    .option("startingOffsets", "latest") \
    .load()

# --- Parse messages ---
parsed_df = kafka_df.select(from_json(col("value").cast("string"), schema_json).alias("data")).select("data.*")

# --- Write to Feast online store in foreachBatch ---
def write_to_online_store(batch_df, batch_id):
    if batch_df.count() == 0:
        return
    pandas_df = batch_df.toPandas()
    print(f"Writing batch {batch_id} with {len(pandas_df)} rows to Feast online store...")
    try:
        store.write_to_online_store(feature_view_name=FEATURE_VIEW_NAME, df=pandas_df)
        print(f"✓ Successfully wrote batch {batch_id} to Feast online store.")
    except Exception as e:
        print(f"✗ Error writing batch {batch_id} to Feast online store: {e}")

# --- Set catalog and schema (from config or defaults) ---
catalog = "temp"  # default as per user instruction
schema = "feature_platform_testing"  # default as per user instruction

# --- Checkpoint location pattern ---
checkpoint_location = os.path.join(
    os.getcwd(),
    "tmp",
    "checkpoints",
    catalog,
    schema,
    FEATURE_VIEW_NAME
)

# --- Start streaming query ---
query = parsed_df.writeStream \
    .foreachBatch(write_to_online_store) \
    .outputMode("append") \
    .option("checkpointLocation", checkpoint_location) \
    .start()

print("Spark Structured Streaming job started. Writing to Feast online store...")
try:
    query.awaitTermination()
except Exception as e:
    print(f"Error during streaming query execution: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
