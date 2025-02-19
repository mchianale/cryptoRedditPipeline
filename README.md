# Reddit Indexing Pipeline for Crypto Trend Analysis

In the fast-paced world of cryptocurrencies, tracking investor sentiment in real time is crucial. This project automates the collection of Reddit posts and comments from crypto-related subreddits, indexing them in Elasticsearch for analysis.

By filtering posts based on relevant keywords, this pipeline helps identify market trends and sentiment shifts. The processed data can be used for monitoring discussions, detecting emerging signals, and supporting data-driven decision-making in the crypto space.

**To run and change config of our current pipeline see `RUN.md`.**

---

## Architecture Overview
### 🔄 **Workflow Diagram**
![global_sch](https://github.com/mchianale/cryptoRedditPipeline/blob/main/doc/currentArchi.png)

Our system automates the collection, processing, and indexing of Reddit data for trend analysis in the cryptocurrency space. Below is an overview of the key components:

### 🕒 **Scheduler Service**
- Checks if the API is available before triggering it.
- Runs the API once per day to fetch new Reddit data.
- Ensures Elasticsearch indices are available and configures mappings if needed.

### 🚀 **Reddit API (FastAPI)**
- Uses PRAW to fetch posts and their associated comments from Reddit.
- Structures the collected data and sends it to Kafka in three distinct topics:
  - **Posts**
  - **Comments**
  - **Replies to comments**

### 🔄 **Kafka (Message Broker)**
- Manages data flow between the API and the indexing pipeline.
- Enables asynchronous message distribution to multiple consumers.

### 🔧 **Logstash Pipeline**
- Consumes messages produced by Kafka.
- Transforms and structures the data for indexing.
- Sends processed data to Elasticsearch.
- Uses separate pipelines for each Kafka topic.

### 📊 **Elasticsearch**
- Stores structured data from Logstash.
- Provides advanced search and analytical capabilities for Reddit posts.
- Enables trend discovery and sentiment analysis in the crypto market.

---

## Kafka & API  

### API - FastAPI  
The `FastAPI-based` API (here `redditAPI`) plays a crucial role in our project by extracting, processing, and sending Reddit data to Kafka. It is responsible for retrieving posts, comments, and replies from the monitored subreddits based on predefined keywords.  

The API exposes several endpoints, including a **health check** to ensure its availability and an endpoint that fetches and sends Reddit data to Kafka within a specified date range.  

### How is RedditAPI used?  
- In our case, our custom `FastAPI` interacts with the **Reddit API** to retrieve data by searching for new **posts** in specified subreddits based on predefined keywords, along with their comments and replies.  
- To update the **subreddits** and **keywords** being tracked, modify the `redditAPI/follow_config.json` file.  
- Our current `redditAPI/follow_config.json` configuration:  

```json
{
    "subreddit_names": ["CryptoCurrency", "CryptoMarkets"],
    "keywords_dict": {
        "bitcoin": ["btc", "bitcoin"],
        "ethereum": ["eth", "ethereum"],
        "dogecoin": ["doge", "dogecoin"],
        "trumpcoin": ["trump", "trumpcoin"],
        "solana": ["sol", "solana"]
    }
}
```

### Kafka Integration  
We have set up a **Kafka cluster** with **three brokers** and **one Zookeeper node**. Having multiple brokers provides resilience and allows us to test Kafka features like replication and failover handling. Zookeeper is used for metadata management, ensuring proper coordination between brokers.  

<p align="center">
  <img src="https://github.com/mchianale/cryptoRedditPipeline/blob/main/doc/kafka.png" alt="global_sch" width="50%">
</p>


### Kafka Topics  
To structure and distribute the data efficiently, we use Kafka **topics**:  
- **`posts`**: Stores information about Reddit posts, including title, text, author, and submission date.  
- **`comments`**: Captures Reddit comments, linking them to their respective posts and tracking the number of replies.  
- **`replies`**: Handles replies to comments, preserving their hierarchical structure.  

Kafka ensures real-time processing and reliable message delivery, enabling seamless downstream consumption of Reddit data for further analysis and insights.  

---

## 🔧 Logstash

Logstash plays a key role in our pipeline by consuming messages from Kafka and sending them to Elasticsearch for indexing and analysis of Reddit data. 

Each type of data (**posts, comments, replies**) is processed separately using three dedicated Logstash instances. Each instance is responsible for consuming a specific Kafka topic and indexing it in Elasticsearch. This separation allows us to apply transformations tailored to each type of message.

### ⚙️ **Logstash General Configuration**
Each Logstash instance runs independently with its own configuration:

```yaml
pipeline.id: main
path.config: "/usr/share/logstash/pipeline"
```

### Parallel Logstash Pipelines
We run three Logstash pipelines in parallel:
- **Logstash** - Posts: Consumes the posts topic and indexes Reddit posts.
- **Logstash** - Comments: Consumes the comments topic and indexes Reddit comments.
- **Logstash** - Replies: Consumes the replies topic and indexes Reddit replies.

All three data types are stored in a single Elasticsearch index (reddit)

---

## Elastic-search
### 🔍 Example Query: Searching Reddit Data in Elasticsearch
To search for posts containing specific keywords (e.g., **Bitcoin BTC**) in our indexed Reddit data, we can use the following **Elasticsearch query**:

```bash
curl -X GET "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "match": {
      "text": "bitcoin btc"
    }
  }
}'
```
- This query searches for documents in the `reddit index` where the text field contains the terms "bitcoin" or "btc"
- In our case, this query returned `632` documents, highlighting that Bitcoin (BTC) is a highly discussed topic in the CryptoCurrency subreddit.

---

## Run a Spark job
1. First, create a new .py job for Spark. See this example.
2. Copy your job script to the Spark master container:
```bash
docker cp ./spark/job.py spark-master:/opt/bitnami/spark/job.py     
```
3. Run the job using Spark:
```bash
docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit --master spark://spark-master:7077 --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.6.2 /opt/bitnami/spark/job.py  
```

In `docker-compose`, **Spark and Elasticsearch** are on the same network to allow Spark to read data from Elasticsearch and write new indices back.

For example, we use Spark to count word occurrences from our Reddit API dataset and store the results in a new Elasticsearch index.

<p align="center">
  <img src="https://github.com/mchianale/cryptoRedditPipeline/blob/main/doc/most_frequent_words.png" alt="global_sch" width="50%">
</p>

---

## Source
- [Kafka Development With Docker](https://jaehyeon.me/blog/2023-05-04-kafka-development-with-docker-part-1/)


