from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Verify CSVs with Spark").getOrCreate()

try:
    print("📘 Reading edfi_school.csv...")
    school_df = spark.read.option("header", "true").csv("edfi_school.csv")
    school_df.show(5)

    print("📗 Reading edfi_student.csv...")
    student_df = spark.read.option("header", "true").csv("edfi_student.csv")
    student_df.show(5)

    print("📙 Reading edfi_studentschoolassociation.csv...")
    assoc_df = spark.read.option("header", "true").csv("edfi_studentschoolassociation.csv")
    assoc_df.show(5)
except Exception as e:
    print(f"❌ CSV read test failed: {e}")
finally:
    spark.stop()
