# Title du projet 
presentation etc...

To run and change config of our current pipeline see `RUN.md`.

---

## Summary

---

## Current Architecture
![global_sch](https://github.com/mchianale/cryptoRedditPipeline/blob/main/doc/currentArchi.png)

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

## Logstash
regarde dans folder logstash les fichier conf modifiable etc..

---

## Elastic-search
### Data & Mappings
### Queries

---

## Run a Spark job
- First create a new `.py` job for spark, see [dd](dd).
- After, copy your job in spark-master:
```bash
docker cp ./spark/job.py spark-master:/opt/bitnami/spark/job.py     
```
- Now run it:
```bash
docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit --master spark://spark-master:7077 --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.6.2 /opt/bitnami/spark/job.py  
```

In `docker-compose`, **sparks** had same network as **elatsic-search** to retrieve elatsic search data and from spark job create a new index.
For example we have use spark to get occurences by word in our reddit API:
---

## Source
- [Kafka Development With Docker](https://jaehyeon.me/blog/2023-05-04-kafka-development-with-docker-part-1/)



docker cp ./spark/job.py spark-master:/opt/bitnami/spark/job.py     

docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit --master spark://spark-master:7077 --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.6.2 /opt/bitnami/spark/job.py
