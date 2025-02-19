from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col, lower
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define stopwords (hardcoded for performance, avoiding nltk overhead)
STOP_WORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
])

# Initialize Spark session
spark = (
    SparkSession.builder.appName("ElasticsearchSparkJob")
    .config("spark.es.nodes", "elasticsearch")  # Elasticsearch hostname
    .config("spark.es.port", "9200")
    .config("spark.es.nodes.wan.only", "true")  # Important for Docker environments
    .getOrCreate()
)
logging.info("-" * 100)
logging.info("STARTING A NEW JOB")
logging.info("-" * 100)
logging.info("Spark session initialized")

# Read data from Elasticsearch
df = (
    spark.read.format("org.elasticsearch.spark.sql")
    .option("es.resource", "reddit")
    .load()
)
logging.info("Data read from Elasticsearch")

# Process text data
df = df.select(lower(col("text")).alias("text"))
words_df = df.select(explode(split(col("text"), "\\W+")).alias("word"))
words_filtered = words_df.filter(
    (col("word") != "") & (~col("word").isin(STOP_WORDS)) & (col("word").rlike("[a-zA-Z]+"))
)
word_count = words_filtered.groupBy("word").count().orderBy(col("count").desc())

# Display top words
logging.info("Most frequent words:")
top_words = word_count.limit(20).collect()
for row in top_words:
    logging.info(f"Word: {row['word']}, Count: {row['count']}")

# Write results back to Elasticsearch
word_count.write.format("org.elasticsearch.spark.sql")\
    .option("es.resource", "reddit_word_count")\
    .option("es.nodes", "elasticsearch")\
    .option("es.port", "9200")\
    .mode("overwrite")\
    .save()

logging.info("Data written to Elasticsearch successfully!")

# Stop Spark session
spark.stop()
logging.info("Spark session stopped")
logging.info("-" * 100)
