import re

def run_sql_file(spark, sql: str, output_path: str = None) -> int:
    # 1. Strip comments (anything after -- until end of line)
    cleaned_sql = re.sub(r'--.*', '', sql)

    # 2. Split cleaned SQL into individual statements
    statements = [
        stmt.strip()
        for stmt in cleaned_sql.split(";")
        if stmt.strip()
    ]

    row_count = 0

    for stmt in statements:
        spark.sql(stmt)

        if output_path and "create or replace temp view" in stmt.lower():
            match = re.search(r"create\s+or\s+replace\s+temp\s+view\s+(\w+)", stmt, re.IGNORECASE)
            if match:
                view_name = match.group(1)
                print(f"💾 Writing view '{view_name}' to '{output_path}'...")
                df = spark.table(view_name)
                df.write.mode("overwrite").option("compression", "snappy").parquet(output_path)
                row_count = df.count()
                print(f"📊 Preview of view '{view_name}':")
                df.show(5)
            else:
                print("⚠️ Could not extract view name from SQL statement.")

    return row_count
