def run_sql_file(spark, sql: str, output_path: str = None) -> int:
    statements = [
        stmt.strip()
        for stmt in sql.split(";")
        if stmt.strip() and not stmt.strip().startswith("--")
    ]

    row_count = None

    for stmt in statements:
        spark.sql(stmt)
        if stmt.lower().startswith("create or replace temp view") and output_path:
            view_name = stmt.split()[5]
            print(f"💾 Writing view '{view_name}' to '{output_path}'...")
            df = spark.table(view_name)
            df.write.mode("overwrite").option("compression", "snappy").parquet(output_path)
            row_count = df.count()

    return row_count or 0
