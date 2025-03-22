import sys
import os

# 🛠 Add project root to Python path BEFORE other imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
from pyspark.sql import SparkSession
from pipelines.pipeline import PipelineExecutor


def main():
    # 🛠 Add project root to Python path BEFORE other imports
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    # 💬 Grab YAML path from CLI or use default
    yaml_path = sys.argv[1] if len(sys.argv) > 1 else "pipelines/flows/pipelines_config.yaml"

    # 💡 Start Spark WITHOUT Delta — we're team Parquet now, baby
    spark = SparkSession.builder \
        .appName("EdFi Flexible Pipeline") \
        .getOrCreate()

    try:
        # 📖 Load YAML config
        with open(yaml_path) as f:
            config = yaml.safe_load(f)

        # 🚀 Run pipeline
        executor = PipelineExecutor(spark, config)
        executor.run()

        # 📋 Show logs
        print("\n=== Pipeline Log ===")
        for log in executor.log:
            print(log)

    except Exception as e:
        print("💥 Pipeline crashed like a diva with no coffee!")
        print(f"Error: {str(e)}")
    finally:
        spark.stop()  # Always clean up, darling

if __name__ == "__main__":
    main()
