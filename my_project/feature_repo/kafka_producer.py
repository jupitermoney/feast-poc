from kafka import KafkaProducer
import json
import time

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

    producer = create_kafka_producer(BOOTSTRAP_SERVERS)

    if producer:
        # Send a few example messages
        for i in range(3):
            message = {'id': i, 'value': f'test_message_{i}', 'timestamp': time.time()}
            send_json_message(producer, TOPIC_NAME, message)
            time.sleep(1)

        producer.flush() # Ensure all messages are sent
        producer.close()
        print("Kafka producer closed.")
    else:
        print("Failed to create Kafka producer. Exiting.") 