# note to run the queries, you need to have the elasticsearch instance running
# and ensure that you have os that have curl installed
# here the command to install it on ubuntu based system using apt package manager
# sudo apt install curl
# here the command to install it on windows system using choco package manager
# choco install curl
# or you canuse WSL
# query to fetch all the documents where text has the word "Bitcoin"
# query to fetch all the documents where text has the word "Bitcoin"
curl -X POST "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "match": {
      "text": "Bitcoin"
    }
  }
}'

# query to aggregate the number of posts per subject
curl -X POST "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "size": 0,
  "aggs": {
    "posts_per_subject": {
      "terms": {
        "field": "subject.keyword"
      }
    }
  }
}'

# query that uses the ngram field to search for the word "Bitc" in the text field
curl -X POST "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "match": {
      "text.ngram": "Bitc"
    }
  }
}'

# query that uses fuzzy search to search for the word "Ethereeum" in the text field
curl -X POST "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "fuzzy": {
      "text.fuzzy": {
        "value": "Ethereeum",
        "fuzziness": "AUTO"
      }
    }
  }
}'

# time series query that retrieves posts created in the last 7 days
curl -X POST "http://localhost:9200/reddit/_search?pretty" -H "Content-Type: application/json" -d '
{
  "query": {
    "range": {
      "submission_date": {
        "gte": "now-7d/d",
        "lte": "now/d",
        "format": "strict_date_optional_time"
      }
    }
  }
}'