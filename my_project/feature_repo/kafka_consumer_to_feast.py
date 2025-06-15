from kafka import KafkaConsumer
import json
import pandas as pd
from feast import FeatureStore, StreamFeatureView, Field, ValueType
from feast.data_source import KafkaSource
from datetime import datetime

# --- Configuration ---
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'my-topic'
# IMPORTANT: This path should point to your feature repository directory,
# which contains your feature_store.yaml and feature view definitions.
# 'my_project/feature_repo' is relative to your workspace root.
FEAST_REPO_PATH = 'my_project/feature_repo'

# --- Initialize Feast FeatureStore ---
try:
    store = FeatureStore(repo_path=FEAST_REPO_PATH)
    print(f"Feast FeatureStore initialized from {FEAST_REPO_PATH}")
except Exception as e:
    print(f"Error initializing Feast FeatureStore: {e}")
    print("Please ensure FEAST_REPO_PATH is correct and feature_store.yaml exists.")
    exit()

# --- Retrieve the StreamFeatureView ---
# This assumes you have a StreamFeatureView named 'driver_hourly_stats_stream'
# defined in your feature repository (e.g., in example_repo.py or similar).
# If not, you'll need to define it first.
try:
    sfv = store.get_stream_feature_view("driver_hourly_stats_stream")
    print(f"Retrieved StreamFeatureView: {sfv.name}")
except Exception as e:
    print(f"Error retrieving StreamFeatureView 'driver_hourly_stats_stream': {e}")
    print("Please ensure this StreamFeatureView is defined in your feature repository.")
    exit()

# --- Kafka Consumer Setup ---
try:
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[BOOTSTRAP_SERVERS],
        auto_offset_reset='earliest', # Start consuming from the beginning if no offset is committed
        enable_auto_commit=True,
        group_id='feast-online-ingest-consumer-group', # Unique consumer group ID
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(f"Kafka consumer started for topic: {TOPIC_NAME} on {BOOTSTRAP_SERVERS}")
except Exception as e:
    print(f"Error creating Kafka consumer: {e}")
    exit()

# --- Consume messages and write to Feast Online Store ---
print("Listening for messages...")
for message in consumer:
    raw_data = message.value
    print(f"\nReceived message from Kafka: {raw_data}")

    try:
        # Prepare data for Feast:
        # The DataFrame must have columns that match the feature view's entities and features,
        # plus an 'event_timestamp' column.
        # This example assumes your Kafka messages contain 'driver_id', 'event_timestamp' (ISO format),
        # and 'conv_rate'. Adjust based on your actual Kafka message structure.
        features_data = {
            "driver_id": [raw_data.get("driver_id")],
            "event_timestamp": [datetime.fromisoformat(raw_data.get("event_timestamp").replace('Z', '+00:00'))], # Convert ISO string to datetime
            "conv_rate": [raw_data.get("conv_rate")],
            # Add other features as defined in your 'driver_hourly_stats_stream' StreamFeatureView
        }
        features_df = pd.DataFrame(features_data)

        # Write to Feast Online Store
        store.write_to_online_store(
            feature_view=sfv,
            df=features_df,
        )
        print(f"Successfully wrote features for driver_id {raw_data.get('driver_id')} to online store.")

    except Exception as e:
        print(f"Error processing message or writing to online store: {e}")
        print(f"Message content that caused error: {raw_data}")

# Clean up (this part might not be reached in a continuous consumer)
consumer.close()
print("Kafka consumer closed.") 