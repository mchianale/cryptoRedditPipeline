from pyspark.sql import SparkSession
from pyspark.sql.functions import col

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

# Perform some transformations (example: filter by subject and select specific columns)
processed_df = df.filter(col("subject") == "bitcoin").select(
    "author", "text", "submission_date", "subject"
)
print(processed_df.show())
print(processed_df.count())

# Write the processed data back to Elasticsearch
processed_df.write.format("org.elasticsearch.spark.sql").option(
    "es.resource", "processed_reddit/_doc"
).mode("overwrite").save()
print("Data written to Elasticsearch")

# Stop Spark session
spark.stop()
logging.info("Spark session stopped")
logging.info("-" * 100)
