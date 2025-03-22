#!/bin/bash

# Ensure the script exits on any error
set -e

# Variables
SPARK_VERSION="3.5.0"
DELTA_VERSION="3.1.0"  # Change this to the appropriate Delta Lake version
SCRIPT_NAME="scripts/test_delta.py"
REPOSITORIES="https://repo1.maven.org/maven2,https://repo.maven.apache.org/maven2,https://packages.databricks.com/maven"
# Clean Ivy cache to prevent conflicts
echo "Cleaning local Ivy cache..."
rm -rf ~/.ivy2/cache
rm -rf ~/.ivy2/jars

# Run the Spark job
echo "Running the Spark job..."
spark-submit \
  --packages io.delta:delta-core_2.12:$DELTA_VERSION \
  --repositories $REPOSITORIES \
  $SCRIPT_NAME

# Final message
echo "Script execution completed successfully!"