# La pipeline actuelle :

**1. API -> Kafka**
- voir reddiAPI, je ferais la doc plus tard (mais ca renvoient en producton kafka plusieurs types d'objets (topics) => les posts, les commentaires et les replies)
- toutes les minuits (avec `schedulerService`), notre API (qui appel Reddit API) est appelé, l'API joue un rôle de producer pour `Kafka`.
  
**2. Logstash**
- `Logstash` run en backgroup (container special), selon les configs donnés (voir `logstash/pipeline` et `logstash/pipeline.yml`)
- Les configs logstash envoient les messages kafka vers elatsic-search (pour chaque topic kafka)

# Pour run
fihcier `.env` à mettre en root:
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

```bash
docker-compose up -d
```
- Data persistents
- Parfois les block Kafka pètent jsp poruqoi mais ca va !
- pas besoin de creer à l'avnace un topic kafka 

---

# A faire
- Je vais faire la documentation de ce que j'ai fais
- LEs données vont bien sur elatsic serahc mais il faut faire des pre mapping (les mapping sont creer automtiquement sinon c pas optimal)
- Réaliser des requêtes dans Elasticsearch :
o 1 requête textuelle
o 1 requêtes comprenant une aggrégation
o 1 requête N-gram.
o 1 requêtes floues (fuzzy).
o 1 série temporelle.
- Visu avec kibana
- apres hadoop u spark pour faire MapReduce 
---

# Source 



=> ANcien readme.md ici:

# API to kafka
## call the API and produced at the same time
**POST** `http://localhost:8000/send_data`
## check if data was produced in kafka
For example in the first broker :
```bash
docker exec -it kafka-0 bash
cd /opt/bitnami/kafka/bin/
./kafka-console-consumer.sh --bootstrap-server kafka-0:9092 --topic submissions --from-beginning
```

# kafka
```bash
docker-compose up -d
```

# Create a new topic
```bash
docker exec -it kafka-0 bash
# in the container
cd /opt/bitnami/kafka/bin/
# create a new topic, here 'submissions'
kafka-topics.sh \
--bootstrap-server localhost:9092 --create \
--topic submissions --partitions 3 --replication-factor 3
# create a new topic, here 'comments'
kafka-topics.sh \
--bootstrap-server localhost:9092 --create \
--topic comments --partitions 3 --replication-factor 3
# create a new topic, here 'replies'
kafka-topics.sh \
--bootstrap-server localhost:9092 --create \
--topic replies --partitions 3 --replication-factor 3
# list all existing topics 
./kafka-topics.sh --list --bootstrap-server localhost:9092
# exit
exit
# you can check, all data is duplicate in others brokers
```

**Warning**

to shut down kafka brokers :
```bash
docker compose down --remove-orphans
```



 
# a faire 
# sources
