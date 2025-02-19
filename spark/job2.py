from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, avg
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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


# Perform some transformations (example: filter by subject and calculate average text length)
filtered_df = df.filter(col("subject") == "bitcoin")
average_text_length = filtered_df.select(avg(length(col("text")))).collect()[0][0]
logging.info(f"Average text length for 'bitcoin' subject: {average_text_length}")

# Stop Spark session
spark.stop()
logging.info("Spark session stopped")
logging.info("-" * 100)
