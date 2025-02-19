from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, avg

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

# Perform some transformations (example: filter by subject and calculate average text length)
filtered_df = df.filter(col("subject") == "bitcoin")
average_text_length = filtered_df.select(avg(length(col("text")))).collect()[0][0]
print(f"Average text length for 'bitcoin' subject: {average_text_length}")

# Write the processed data back to Elasticsearch (optional)
# Here we create a DataFrame with the result and write it back to Elasticsearch
result_df = spark.createDataFrame(
    [("bitcoin", average_text_length)], ["subject", "average_text_length"]
)
result_df.write.format("org.elasticsearch.spark.sql").option(
    "es.resource", "processed_reddit/_doc"
).mode("overwrite").save()
print("Data written to Elasticsearch")

# Stop the Spark session
spark.stop()

# to run the job, use the following command:
# spark-submit --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0 ./spark/job.py
