import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, LongType

# The default location for the quickstart parquet file
parquet_file_path = "./data/driver_stats.parquet"

try:
    df = pd.read_parquet(parquet_file_path)
    print(df.head()) # Print the first 5 rows
    print(df.info()) # Print a summary of the DataFrame (columns, types, non-null values)
except FileNotFoundError:
    print(f"Error: The file '{parquet_file_path}' was not found. Make sure you are in the 'my_project/feature_repo' directory.")
except Exception as e:
    print(f"An error occurred: {e}")

# Configure SparkSession for Delta Lake
spark = SparkSession.builder \
    .appName("DeltaLakeRead") \
    .config("spark.jars.packages", "io.delta:delta-spark_2.13:4.0.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Set log level to INFO for more detailed output
spark.sparkContext.setLogLevel("INFO")

try:
    delta_table_path = "my_project/feature_repo/data/sms"
    df_delta = spark.read.format("delta").load(delta_table_path)
    print("\n--- SMS Delta Table Data (using Spark) ---")
    print(df_delta.limit(5).toPandas()) # Print the first 5 rows after converting to Pandas
    df_delta.printSchema() # Print a summary of the DataFrame (columns, types)
except Exception as e:
    print(f"An error occurred while trying to read the SMS Delta Table with Spark: {e}")
finally:
    spark.stop() # Stop the SparkSession 