@echo off
curl -X POST "http://localhost:9200/posts/_search?pretty" -H "Content-Type: application/json" -d "{ \"query\": { \"match\": { \"text\": \"Bitcoin\" } } }"
curl -X POST "http://localhost:9200/posts/_search?pretty" -H "Content-Type: application/json" -d "{ \"size\": 0, \"aggs\": { \"posts_per_category\": { \"terms\": { \"field\": \"category.keyword\" } } } }"
curl -X POST "http://localhost:9200/posts/_search?pretty" -H "Content-Type: application/json" -d "{ \"query\": { \"match\": { \"text.ngram\": \"Bitc\" } } }"
curl -X POST "http://localhost:9200/posts/_search?pretty" -H "Content-Type: application/json" -d "{ \"query\": { \"fuzzy\": { \"text\": { \"value\": \"BTC\", \"fuzziness\": \"AUTO\" } } } }"
curl -X POST "http://localhost:9200/posts/_search?pretty" -H "Content-Type: application/json" -d "{ \"query\": { \"range\": { \"submission_date\": { \"gte\": \"now-7d/d\", \"lte\": \"now/d\", \"format\": \"strict_date_optional_time\" } } } }"
pause
