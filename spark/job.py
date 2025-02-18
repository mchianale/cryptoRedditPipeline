from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = (
    SparkSession.builder.appName("ElasticsearchSparkJob")
    .config(
        "spark.es.nodes", "elasticsearch"
    )  # Elasticsearch hostname change it to localhost if you are running it locally
    .config("spark.es.port", "9200")
    .getOrCreate()
)
print("Spark session initialized")

# Read data from Elasticsearch
df = (
    spark.read.format("org.elasticsearch.spark.sql")
    .option("es.resource", "reddit/_doc")
    .load()
)
print("Data read from Elasticsearch")

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

# Stop the Spark session
spark.stop()

# to run the job, use the following command:
# spark-submit --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0 ./spark/job.py
