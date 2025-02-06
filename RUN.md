# Title du projet 

## 1. Set Up the `.env` File  
In the root of the project, create a `.env` file:
```bash
CLIENT_ID=""
CLIENT_SECRET=""
REDDIT_USERNAME=""
REDDIT_SECRET=""
USER_AGENT=""
# Kafka  Configuration (Inside Docker Network)
KAFKA_BROKERS = "kafka-0:9092,kafka-1:9092,kafka-2:9092"
# our API endpoint
HEALTH_ENDPOINT = "http://reddit-api:8000/health_check"
SEND_ENDPOINT = "http://reddit-api:8000/send_data"
# To ping elastic-search
ES_ENDPOINT = "http://elasticsearch:9200"
# Trigger configuration "HH:mm"
REQUEST_NEW_DATA_HOURS = "18:00" 
```

- Fill in the Reddit API credentials: To manage them, go [here](https://ssl.reddit.com/prefs/apps/).
- `REQUEST_NEW_DATA_HOURS`: Defines the time (**HH:mm**) when `redditAPI` will be automatically triggered by `schedulerService`.

## 2. Run Everything Using Docker
To start all services in detached mode, run:
```bash
docker-compose up -d
```

