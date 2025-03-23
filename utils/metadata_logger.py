# utils/metadata_logger.py

import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import (
    StructType, StructField,
    StringType, TimestampType, DoubleType
)

class MetadataLogger:
    def __init__(self, spark: SparkSession, table_path: str):
        """
        A logger to capture pipeline events in a structured Parquet table.
        """
        self.spark = spark
        self.table_path = table_path

        self.schema = StructType([
            StructField("batch_id", StringType(), True),
            StructField("pipeline_name", StringType(), True),
            StructField("step_name", StringType(), True),
            StructField("event", StringType(), True),
            StructField("duration_sec", DoubleType(), True),
            StructField("error_message", StringType(), True),
        ])

    def log_event(
        self,
        batch_id: str,
        pipeline_name: str,
        step_name: str,
        event: str,
        duration_sec: float = None,
        error_message: str = None,
    ):
        """
        Appends a log record to a Parquet file.
        """
        logging.info(
            f"[MetadataLogger] {event} for {step_name or pipeline_name} "
            f"(batch_id={batch_id}, duration={duration_sec}, error={error_message})"
        )

        try:
            data = [
                (
                    batch_id,
                    pipeline_name,
                    step_name,
                    event,
                    duration_sec,
                    error_message
                )
            ]

            df = self.spark.createDataFrame(data, self.schema)
            df = df.withColumn("timestamp", current_timestamp())

            # Reorder columns just for ✨aesthetic✨ if you want
            columns = ["timestamp"] + [c for c in df.columns if c != "timestamp"]
            df = df.select(columns)

            df.write \
              .format("parquet") \
              .mode("append") \
              .save(self.table_path)

        except Exception as e:
            logging.warning(f"[MetadataLogger] Logging failed: {e}")
