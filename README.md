

# kafka
```bash
docker-compose up -d
```

```
docker exec -it kafka bash
```

kafka-topics --create --topic topics --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
kafka-topics --list --bootstrap-server kafka:9092
