# Reddit Indexing Pipeline for Crypto Trend Analysis

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

---

## 2. Run Everything Using Docker
To start all services in detached mode, run:
```bash
docker-compose up -d
```

---

## 🛠️ Check if Data is Produced in Kafka
To verify that messages are correctly produced in Kafka, you can consume messages from a topic.  
For example, to check messages in the **first broker (`kafka-0`)** for the `posts` topic:

```bash
docker exec -it kafka-0 bash
cd /opt/bitnami/kafka/bin/
./kafka-console-consumer.sh --bootstrap-server kafka-0:9092 --topic posts --from-beginning
```

## 🛠️ Check if Messages are Consumed from Kafka
To verify that Logstash or other consumers are successfully consuming messages from Kafka, you can check the consumer group offsets.

1. First, list all consumer groups:
```bash
docker exec -it kafka-0 bash
kafka-consumer-groups.sh --bootstrap-server kafka-0:9092 --list
```

2. First, list all consumer groups:
```bash
kafka-consumer-groups.sh --bootstrap-server kafka-0:9092 --group logstash --describe
```

- `CURRENT-OFFSET` → Number of messages processed by the consumer.
- `LOG-END-OFFSET` → Total messages in the topic.
- `LAG` → Difference between the two (messages waiting to be processed).
  
If `LAG` is growing continuously, your consumers might not be processing messages correctly.
If everything is working, the offsets should be updating dynamically as new messages arrive.

