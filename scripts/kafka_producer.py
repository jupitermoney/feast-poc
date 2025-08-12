from kafka import KafkaProducer
import json
import time
import pandas as pd

def create_kafka_producer(bootstrap_servers: str):
    """
    Creates and returns a KafkaProducer instance.
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Kafka producer created successfully for servers: {bootstrap_servers}")
        return producer
    except Exception as e:
        print(f"Error creating Kafka producer: {e}")
        return None

def send_json_message(producer: KafkaProducer, topic: str, message: dict):
    """
    Sends a JSON message to the specified Kafka topic.
    """
    try:
        future = producer.send(topic, message)
        record_metadata = future.get(timeout=10) # Block until a single message is sent
        print(f"Successfully sent message to topic {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    BOOTSTRAP_SERVERS = 'localhost:9092'
    TOPIC_NAME = 'my-topic'
    # Define the path to your parquet file
    # Assuming data directory is inside my_project/feature_repo/
    stream_parquet_file_path = "../my_project/feature_repo/data/driver_stats_stream.parquet"

    producer = create_kafka_producer(BOOTSTRAP_SERVERS)

    if producer:
        try:
            print("Reading parquet")
            df = pd.read_parquet(stream_parquet_file_path).sort_values(by="event_timestamp")
            print("Emitting events")
            iteration = 1
            for row in df[
                ["driver_id", "event_timestamp", "created", "conv_rate", "acc_rate"]
            ].to_dict("records"):
                # Make event one more year recent to simulate fresher data
                row["event_timestamp"] = (
                    row["event_timestamp"] + pd.Timedelta(weeks=52 * iteration)
                ).strftime("%Y-%m-%d %H:%M:%S")
                row["created"] = row["created"].strftime("%Y-%m-%d %H:%M:%S")
                send_json_message(producer, TOPIC_NAME, row)
                print(row)
                # time.sleep(1.0)
                break
                

        except FileNotFoundError:
            print(f"Error: Parquet file not found at {stream_parquet_file_path}. Please ensure it exists.")
        except Exception as e:
            print(f"Error reading Parquet file or sending messages: {e}")
        finally:
            # This part will not be reached in the current infinite loop setup
            # unless an exception occurs. Consider how you want to handle graceful shutdown.
            producer.flush() # Ensure all messages are sent
            producer.close()
            print("Kafka producer closed.")
    else:
        print("Failed to create Kafka producer. Exiting.") 