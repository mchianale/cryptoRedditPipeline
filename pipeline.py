import time
import requests
#import schedule
import logging
import docker
from confluent_kafka import Consumer, KafkaException
from dotenv import load_dotenv
import os
import datetime 

# Configure Logging
logging.basicConfig(filename="pipeline_logs/kafka_logstash_manager.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Kafka & API Configuration
# Load environment variables from the .env file
load_dotenv()
KAFKA_BROKERS = os.environ["KAFKA_BROKERS"]
KAFKA_TOPICS = os.environ["KAFKA_TOPICS"]
API_ENDPOINT = os.environ["API_ENDPOINT"]
LOGSTASH_IMAGE = os.environ["LOGSTASH_IMAGE"]
KAFKA_NETWORK = os.environ["KAFKA_NETWORK"]

# Kafka Consumer Configuration
consumer_conf = {
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'logstash-trigger-group',
    'auto.offset.reset': 'earliest'
}

# Initialize Docker Client
docker_client = docker.from_env()

def send_data_to_kafka():
    """ Calls the FastAPI endpoint to send new data to Kafka """
    try:
        logging.info("Triggering API to send data to Kafka...")
        url = f"{API_ENDPOINT}?end_date={str(datetime.datetime.today().date()).replace('-', '/')}"
        logging.info(f"Calling: {url}...")
        response = requests.post(url)
        if response.status_code == 200:
            logging.info("Data sent successfully to Kafka")
            logging.info(f"Response: {response.text}")
        else:
            logging.error(f"Failed to send data: {response.status_code} {response.text}")
    except Exception as e:
        logging.error(f"Error sending data: {e}")

def check_kafka_for_new_messages():
    """ Checks if new messages are in Kafka and triggers Logstash """
    try:
        logging.info(f"Load consumer using conf={consumer_conf}...")
        consumer = Consumer(consumer_conf)
        logging.info(f"Trying to subscribe to {KAFKA_TOPICS}...")
        consumer.subscribe('posts')

        logging.info("Checking Kafka for new messages...")

        while True:
            msg = consumer.poll(timeout=5.0)  # Poll for new messages

            if msg is None:
                break  # No new messages

            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    logging.error(f"Kafka error: {msg.error()}")
                    break
            
            logging.info(f"New data detected in Kafka topic: {msg.topic()}")
            trigger_logstash(msg.topic())  # Start Logstash when new data arrives

        consumer.close()
    except Exception as e:
        logging.error(f"Error checking Kafka: {e}")

def trigger_logstash(topic):
    """ Starts a new Logstash container when new Kafka messages are detected """
    container_name = f"logstash-{topic}"

    logging.info(f"Starting Logstash for topic: {topic}")

    try:
        # Stop and remove existing Logstash container for this topic
        try:
            old_container = docker_client.containers.get(container_name)
            old_container.stop()
            old_container.remove()
            logging.info(f"Old Logstash container removed: {container_name}")
        except docker.errors.NotFound:
            logging.info(f"No previous Logstash container found for {topic}")

        # Run a new Logstash container
        docker_client.containers.run(
            image=LOGSTASH_IMAGE,
            name=container_name,
            detach=True,
            networks=["kafka-network"],
            environment={
                "LS_JAVA_OPTS": "-Xms512m -Xmx512m",
                "KAFKA_BROKER": KAFKA_BROKERS,
                "KAFKA_TOPIC": topic,
                "ELASTICSEARCH_HOST": "elasticsearch:9200"
            },
            volumes={
                ".logstash/logstash.conf": {"bind": "/usr/share/logstash/pipeline/logstash.conf", "mode": "ro"}
            }
        )
        logging.info(f"Logstash container started for topic {topic}")
    except Exception as e:
        logging.error(f"Error starting Logstash for {topic}: {e}")


#send_data_to_kafka()
check_kafka_for_new_messages()