from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, expr
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from feast import FeatureStore
import pandas as pd
import os
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

# --- Initialize Spark Session ---
spark = SparkSession.builder \
    .master("local") \
    .appName("feast-spark") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
    .getOrCreate()

# Set shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", 5)

# --- Initialize Feast FeatureStore ---
store = FeatureStore(repo_path=FEAST_REPO_PATH)

# --- Define Schema for Kafka Messages ---
schema = StructType([
    StructField("driver_id", StringType(), True),
    StructField("event_timestamp", TimestampType(), True),
    StructField("created", TimestampType(), True),
    StructField("conv_rate", DoubleType(), True),
    StructField("acc_rate", DoubleType(), True),
    StructField("avg_daily_trips", IntegerType(), True)
])

# --- Read from Kafka ---
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) \
    .option("subscribe", TOPIC_NAME) \
    .option("startingOffsets", "latest") \
    .load()

# --- Parse JSON from Kafka ---
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Transform the data to match feature view schema
transformed_df = parsed_df \
    .withColumn("conv_percentage", col("conv_rate") * 100.0) \
    .withColumn("acc_percentage", col("acc_rate") * 100.0) \
    .drop("conv_rate", "acc_rate")

# --- Process each batch ---
def process_batch(batch_df, batch_id):
    if batch_df.isEmpty():
        return
    
    # Convert Spark DataFrame to Pandas
    pandas_df = batch_df.toPandas()
    
    # Ensure timestamp columns are in the correct format
    pandas_df['event_timestamp'] = pd.to_datetime(pandas_df['event_timestamp'])
    pandas_df['created'] = pd.to_datetime(pandas_df['created'])
    
    # Log the data being written
    logging.info(f"Writing batch {batch_id} to Feast online store")
    logging.info(f"Data preview:\n{pandas_df.head()}")
    
    # Write to Feast online store
    store.write_to_online_store(
        feature_view_name="driver_hourly_stats_stream",
        df=pandas_df
    )
    
    print(f"Processed batch {batch_id} with {len(pandas_df)} records")

# --- Start the streaming query ---
query = transformed_df.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .trigger(processingTime="30 seconds") \
    .start()

print("Spark Structured Streaming job started. Listening for Kafka messages...")
query.awaitTermination() 