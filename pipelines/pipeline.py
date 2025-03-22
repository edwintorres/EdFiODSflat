import os
import time
import traceback
from utils.sql_loader import render_sql
from utils.sql_runner import run_sql_file
from utils.dq_checks import run_dq_checks


class PipelineExecutor:
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.log = []

    def run(self):
        steps = self.config["groups"][0]["steps"]
        for step in steps:
            self.run_step(step)

    def run_step(self, step):
        retries = step.get("max_retries", 0)
        attempt = 0
        success = False

        while attempt <= retries and not success:
            try:
                print(f"▶ Running step: {step['name']} (attempt {attempt + 1})")
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


                # 🧪 Run DQ Checks ONLY IF SQL runs fine
                if step.get("dq_checks"):
                    print("⏳ Waiting to ensure output files are committed...")
                    time.sleep(2)  # Optional: allow time for files to commit
                    run_dq_checks(self.spark, step["dq_checks"])

                end = time.time()
                print(f"✅ Step succeeded: {step['name']} in {round(end - start, 2)}s")

                self.log.append({
                    "step": step["name"],
                    "status": "success",
                    "duration_sec": round(end - start, 2),
                    "rows": row_count,
                })
                success = True

            except Exception as e:
                traceback.print_exc()
                attempt += 1
                if attempt > retries:
                    print(f"❌ Step FAILED after {attempt} attempts: {step['name']}")
                    self.log.append({
                        "step": step["name"],
                        "status": "failed",
                        "error": str(e),
                    })
