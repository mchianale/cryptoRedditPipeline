import time
import requests
import logging
from dotenv import load_dotenv
import os
import datetime
import schedule

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Configuration
# Load environment variables from the .env file
load_dotenv()
# API endpoints
REDDIT_API = "http://reddit-api:8000"
HEALTH_ENDPOINT = f"{REDDIT_API}/health_check"
SEND_DATA_ENDPOINT = f"{REDDIT_API}/send_data"
# elatsic
ES_ENDPOINT = "http://elasticsearch:9200"
# pieplien hour trigger
REQUEST_NEW_DATA_HOURS = os.environ["REQUEST_NEW_DATA_HOURS"]
# pretty logging
SEP = "-" * 30


def send_data_to_kafka():
    """Calls the FastAPI endpoint to send new data to Kafka"""
    try:
        start_time = time.time()
        logging.info(f"Triggering API to send data to Kafka... {SEP}")
        date_today = datetime.datetime.today().strftime("%d/%m/%Y")
        url = f"{HEALTH_ENDPOINT}?start_date={date_today}&end_date={date_today}"
        logging.info(f"Calling: {url}...")
        response = requests.post(url)
        end_time = time.time()
        duration_minutes = (end_time - start_time) / 60
        if response.status_code == 200:
            logging.info(f"Response: {response.text}")
        else:
            logging.error(
                f"Failed to send data: {response.status_code} {response.text}"
            )
        logging.info(f"Duration of the process: {duration_minutes:.2f} minutes")
        logging.info(f"{SEP}")

    except Exception as e:
        logging.error(f"Error sending data: {e}")
        logging.info(f"{SEP}")


# schedule
# Schedule API Call Every Day at REQUEST_NEW_DATA_HOURS hh:mm
my_schedule = schedule.Scheduler()
my_schedule.every().day.at(REQUEST_NEW_DATA_HOURS).do(send_data_to_kafka)


def check_health(endpoint):
    max_retry = 0

    while max_retry < 30:
        if max_retry == 30:
            raise f"Impossible to ping {endpoint}"
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                logging.info(f"Successfuly ping {endpoint}")
                return True
            else:
                logging.info(f"Trying to ping {endpoint}, retry_number={max_retry}")
                max_retry += 1
        except Exception as e:
            logging.info(
                f"Trying to ping {endpoint}, retry_number={max_retry}, error={str(e)}"
            )
            max_retry += 1
        time.sleep(1)


if __name__ == "__main__":
    # check our fast API is running
    check_health(HEALTH_ENDPOINT)

    # check elastic search is good to
    check_health(ES_ENDPOINT)

    # send_data_to_kafka()
    while True:
        my_schedule.run_pending()
        time.sleep(5)  # Sleep for 5 second to prevent high CPU usage
        # This loop checks if any tasks are scheduled to run
        # and executes them when their time comes.
        # try sending message to kafka (producer)
