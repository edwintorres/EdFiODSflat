import os
import time
import traceback

from utils.sql_loader import render_sql
from utils.sql_runner import run_sql_file
from utils.dq_checks import run_dq_checks
from utils.metadata_logger import MetadataLogger
from datetime import datetime

class PipelineExecutor:
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.log = []

        # 1) Grab pipeline_name from config or default
        self.pipeline_name = self.config.get("pipeline_name", "My_Pipeline")

        # 2) Grab or generate a batch_id
        self.batch_id = self.config.get("batch_id")
        if not self.batch_id:
            # e.g. fallback to a timestamp-based ID
            self.batch_id = datetime.now().strftime("auto_%Y%m%d_%H%M%S")

        # 3) Handle checkpoint config
        self.checkpoint_config = self.config.get("checkpoint", {})
        self.checkpoint_enabled = self.checkpoint_config.get("enabled", False)
        self.checkpoint_path = self.checkpoint_config.get("path")

        # Instantiate the metadata logger
        self.metadata_logger = MetadataLogger(
            spark,
            table_path="file://" + os.path.abspath("logs/metadata_logs")
        )

    def run(self):
        """
        Run the entire pipeline from the config.
        """
        # Log pipeline start
        self.metadata_logger.log_event(
            batch_id=self.batch_id,
            pipeline_name=self.pipeline_name,
            step_name=None,
            event="PIPELINE_START",
        )

        # For simplicity, we only show the first group
        # If you have multiple groups, just loop them
        steps = self.config["groups"][0]["steps"]
        for step in steps:
            self.run_step(step)

        # Log pipeline end
        self.metadata_logger.log_event(
            batch_id=self.batch_id,
            pipeline_name=self.pipeline_name,
            step_name=None,
            event="PIPELINE_END",
        )

    def run_step(self, step):
        retries = step.get("max_retries", 0)
        attempt = 0
        success = False
        step_name = step["name"]

        # 4) If checkpoint is enabled, check if this step was done for this batch_id
        if self.checkpoint_enabled and self.is_step_checkpointed(step_name):
            print(f"⚠️ Skipping step '{step_name}' due to existing checkpoint.")
            return

        while attempt <= retries and not success:
            try:
                # Log step start
                self.metadata_logger.log_event(
                    batch_id=self.batch_id,
                    pipeline_name=self.pipeline_name,
                    step_name=step_name,
                    event="STEP_START"
                )
                print(f"▶ Running step: {step_name} (attempt {attempt + 1}), batch_id={self.batch_id}")

                start = time.time()

                # 🪄 Pre-load any view defined in YAML
                pre_view = step.get("pre_view")
                if pre_view:
                    print(f"🔍 Registering pre-view: {pre_view['name']}")
                    reader = self.spark.read.format(pre_view["format"])
                    for key, value in pre_view.get("options", {}).items():
                        reader = reader.option(key, value)
                    df = reader.load(pre_view["path"])
                    df.createOrReplaceTempView(pre_view["name"])
                    print(f"✅ View registered: {pre_view['name']}")

                # 🧠 Load and run SQL
                sql = render_sql(f"sql/{step['script']}", {})
                output_path = step.get("output_path")  # 👈 From YAML
                row_count = run_sql_file(self.spark, sql, output_path)

                # Run DQ checks
                if step.get("dq_checks"):
                    print("⏳ Waiting to ensure output files are committed...")
                    time.sleep(2)  # Optional
                    run_dq_checks(self.spark, step["dq_checks"])

                end = time.time()
                duration_sec = round(end - start, 2)

                print(f"✅ Step succeeded: {step_name} in {duration_sec}s (batch: {self.batch_id})")
                self.log.append({
                    "step": step_name,
                    "status": "success",
                    "duration_sec": duration_sec,
                    "rows": row_count,
                })

                # Log step end
                self.metadata_logger.log_event(
                    batch_id=self.batch_id,
                    pipeline_name=self.pipeline_name,
                    step_name=step_name,
                    event="STEP_END",
                    duration_sec=duration_sec
                )

                # 5) If checkpoint is enabled, mark this step as completed
                if self.checkpoint_enabled:
                    self.save_step_checkpoint(step_name)

                success = True

            except Exception as e:
                traceback.print_exc()
                attempt += 1

                # Log step fail
                self.metadata_logger.log_event(
                    batch_id=self.batch_id,
                    pipeline_name=self.pipeline_name,
                    step_name=step_name,
                    event="STEP_FAIL",
                    error_message=str(e)
                )

                if attempt > retries:
                    print(f"❌ Step FAILED after {attempt} attempts: {step_name}")
                    self.log.append({
                        "step": step_name,
                        "status": "failed",
                        "error": str(e),
                    })

    # -------------------------------------
    # Checkpointing Helper Methods
    # -------------------------------------

    def checkpoint_file_for(self, step_name):
        """
        Returns a path for storing a small marker file.
        e.g. file:/tmp/checkpoints/<pipeline>/<batch_id>/<step_name>.chk
        """
        # If you want to separate pipeline and batch in subdirs:
        # base_dir = f"{self.checkpoint_path}/{self.batch_id}"
        # Or keep it simpler if you prefer
        base_dir = self.checkpoint_path
        return f"{base_dir}/{self.batch_id}_{step_name}.chk"

    def is_step_checkpointed(self, step_name):
        """
        Checks if a checkpoint file exists for the given step + batch.
        """
        marker_path = self.checkpoint_file_for(step_name)
        # Pseudocode: if you're on a local file system, you can do:
        # return os.path.exists(marker_path.replace("file:",""))
        # If you're in a Databricks/HDFS environment, you might do:
        # try: dbutils.fs.ls(marker_path) ...
        if marker_path.startswith("file:"):
            local_path = marker_path.replace("file:", "")
            return os.path.exists(local_path)
        # More sophisticated logic for s3:// or abfss://
        return False

    def save_step_checkpoint(self, step_name):
        """
        Writes a small marker file to indicate this step is done.
        """
        marker_path = self.checkpoint_file_for(step_name)
        if marker_path.startswith("file:"):
            local_path = marker_path.replace("file:", "")
            with open(local_path, "w") as f:
                f.write("done")
        # For cloud or distributed file systems, adapt as needed
