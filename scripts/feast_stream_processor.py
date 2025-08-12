import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from feast import FeatureStore
#from feast.infra.offline_stores.contrib.spark_offline_store.spark import SparkOfflineStore
#from feast.repo_contents import RepoContents
from feast.infra.contrib.stream_processor import ProcessorConfig
from feast.infra.contrib.spark_kafka_processor import SparkProcessorConfig
from feast.infra.contrib.stream_processor import get_stream_processor_object
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Set Feast logger to DEBUG level
logging.getLogger('feast').setLevel(logging.DEBUG)

# --- Configuration ---
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'my-topic'
FEAST_REPO_PATH = "../my_project/feature_repo"

# Set Spark submit arguments
os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 pyspark-shell"

# --- Initialize Feast FeatureStore ---
try:
    store = FeatureStore(repo_path=FEAST_REPO_PATH)
    print(f"Feast FeatureStore initialized from {FEAST_REPO_PATH}")
except Exception as e:
    print(f"Error initializing Feast FeatureStore: {e}")
    print("Please ensure FEAST_REPO_PATH is correct and feature_store.yaml exists.")
    exit()

# --- Retrieve the StreamFeatureView ---
try:
    # This assumes you have a StreamFeatureView named 'driver_hourly_stats_stream'
    sfv = store.get_stream_feature_view("driver_hourly_stats_stream")
    print(f"Retrieved StreamFeatureView: {sfv.name}")
except Exception as e:
    print(f"Error retrieving StreamFeatureView 'driver_hourly_stats_stream': {e}")
    print("Please ensure this StreamFeatureView is defined in your feature repository.")
    exit()

# --- Spark Session Setup ---
# See https://spark.apache.org/docs/3.1.2/structured-streaming-kafka-integration.html#deploying for notes on why we need this environment variable.
os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages=org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 pyspark-shell"
spark = SparkSession.builder.master("local").appName("feast-spark").getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", 5)
spark.sparkContext.setLogLevel("INFO")

def preprocess_fn(rows: pd.DataFrame):
    print(f"df columns: {rows.columns}")
    print(f"df size: {rows.size}")
    print(f"df preview:\n{rows.head()}")
    return rows


ingestion_config = SparkProcessorConfig(mode="spark", source="kafka", spark_session=spark, processing_time="10 seconds", query_timeout=15)

processor = get_stream_processor_object(
    config=ingestion_config,
    fs=store,
    sfv=sfv,
    preprocess_fn=preprocess_fn,
)
query = processor.ingest_stream_feature_view()

print("Spark Structured Streaming job started. Listening for Kafka messages...")
query.awaitTermination() 