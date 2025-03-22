#!/bin/bash

# 🚨 Stop on error
set -e

# 💡 Default to 'bronze' if no arg is given
PIPELINE_NAME=${1:-bronze}
CONFIG_FILE="pipelines/flows/${PIPELINE_NAME}.yaml"

# 🎤 Announce what we're doing
echo "🚀 Running pipeline: $PIPELINE_NAME"
echo "📄 Using config: $CONFIG_FILE"

# 💥 Run the pipeline
python3 pipelines/run_pipeline.py "$CONFIG_FILE"
