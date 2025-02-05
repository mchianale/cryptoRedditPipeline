import time
import requests
import logging
from dotenv import load_dotenv
import os
import datetime 
import schedule

# Configure Logging
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# API Configuration
# Load environment variables from the .env file
load_dotenv()
# API endpoints
HEALTH_ENDPOINT = os.environ["HEALTH_ENDPOINT"]
SEND_ENDPOINT = os.environ["SEND_ENDPOINT"]
#elatsic
ES_ENDPOINT = os.environ["ES_ENDPOINT"]
# pieplien hour trigger
REQUEST_NEW_DATA_HOURS = os.environ["REQUEST_NEW_DATA_HOURS"]
print(REQUEST_NEW_DATA_HOURS)
# pretty logging
SEP = "-"*30

def send_data_to_kafka():
    """ Calls the FastAPI endpoint to send new data to Kafka """
    try:
        start_time = time.time()
        logging.info(f"Triggering API to send data to Kafka... {SEP}")
        url = f"{SEND_ENDPOINT}?end_date={datetime.datetime.today().strftime('%d/%m/%Y')}"
        logging.info(f"Calling: {url}...")
        response = requests.post(url)
        end_time = time.time()
        duration_minutes = (end_time - start_time) / 60
        if response.status_code == 200:
            logging.info(f"Response: {response.text}")
        else:
            logging.error(f"Failed to send data: {response.status_code} {response.text}")
        logging.info(f"Duration of the process: {duration_minutes:.2f} minutes")
        logging.info(f"{SEP}")

    except Exception as e:
        logging.error(f"Error sending data: {e}")
        logging.info(f"{SEP}")

# schedule 
# Schedule API Call Every Day at REQUEST_NEW_DATA_HOURS hh:mm
my_schedule = schedule.Scheduler()
my_schedule.every().day.at(REQUEST_NEW_DATA_HOURS).do(send_data_to_kafka)

if __name__ == "__main__":
    # check our fast API is running
    max_retry = 0
    while True:
        if max_retry == 30:
            raise f"Impossible to ping {HEALTH_ENDPOINT}"
        try:
            response = requests.get(HEALTH_ENDPOINT)
            if response.status_code == 200:
                logging.info(f"Successfuly ping {HEALTH_ENDPOINT}")
                break
            else:
                logging.info(f"Trying to ping {HEALTH_ENDPOINT}, retry_number={max_retry}")
                max_retry += 1
        except Exception as e:
            logging.info(f"Trying to ping {HEALTH_ENDPOINT}, retry_number={max_retry}, error={str(e)}")
            max_retry += 1
        time.sleep(1)

    # check elastic search is good to
    max_retry = 0
    while True:
        if max_retry == 30:
            raise f"Impossible to ping {ES_ENDPOINT}"
        try:
            response = requests.get(ES_ENDPOINT)
            if response.status_code == 200:
                logging.info(f"Successfuly ping {ES_ENDPOINT}")
                break
            else:
                logging.info(f"Trying to ping {ES_ENDPOINT }, retry_number={max_retry}")
                max_retry += 1
        except Exception as e:
            logging.info(f"Trying to ping {ES_ENDPOINT}, retry_number={max_retry}, error={str(e)}")
            max_retry += 1
        time.sleep(2)

    send_data_to_kafka()
    """while True:
        my_schedule.run_pending()
        time.sleep(5)  # Sleep for 5 second to prevent high CPU usage
        #This loop checks if any tasks are scheduled to run
        #and executes them when their time comes.
            # try sending message to kafka (producer)"""
    