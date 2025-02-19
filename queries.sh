# note to run the queries, you need to have the elasticsearch instance running
# and ensure that you have os that have curl installed
# here the command to install it on ubuntu based system using apt package manager
# sudo apt install curl
# here the command to install it on windows system using choco package manager
# choco install curl
# or you canuse WSL


# query to fetch all the documents where text has the word "bitcoin" "btc"
curl -X GET "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "match": {
      "text": "bitcoin btc"
    }
  }
}'

# query to aggregate the number of replies and comments made per hour
curl -X GET "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '{
  "size": 0,
  "query": {
    "terms": {
      "reddit_type.keyword": ["comment", "reply"]
    }
  },
  "aggs": {
    "comments_replies_by_hour": {
      "terms": {
        "script": {
          "source": "doc[\"submission_date\"].value.getHour()",
          "lang": "painless"
        },
        "size": 24,
        "order": { "_key": "asc" }
      },
      "aggs": {
        "count_per_hour": {
          "value_count": { "field": "submission_date" }
        }
      }
    }
  }
}'


# query that uses the ngram field to search for the lemme invest (investissment, invests etc..)
curl -X GET "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "match": {
      "text.ngram": "invest"
    }
  }
}'

# query that uses fuzzy search to search for the word "Ethereeum" in the text field
curl -X GET "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "fuzzy": {
      "text.fuzzy": {
        "value": "ethereum",
        "fuzziness": "AUTO"
      }
    }
  }
}'

# time series query mean score of a reddit type per day
curl -X GET "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "size": 0,
  "aggs": {
    "score_evolution": {
      "date_histogram": {
        "field": "submission_date",
        "calendar_interval": "day"
      },
      "aggs": {
        "avg_score": {
          "avg": {
            "field": "score"
          }
        },
        "sorted_buckets": {
          "bucket_sort": {
            "sort": [{ "avg_score.value": { "order": "desc" } }] 
          }
        }
      }
    }
  }
}'
