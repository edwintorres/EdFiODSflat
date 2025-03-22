from pyspark.sql import SparkSession

# Initialize Spark session with Delta Lake extensions
spark = SparkSession.builder \
    .appName("DeltaQuickTest") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Write data to Delta format
spark.range(5).write.format("delta").mode("overwrite").save("data/test_delta")

# Read data back from Delta format
df = spark.read.format("delta").load("data/test_delta")

# Show the data
df.show()

# Perform additional operation: Count the number of rows
row_count = df.count()
print(f"Number of rows in Delta table: {row_count}")