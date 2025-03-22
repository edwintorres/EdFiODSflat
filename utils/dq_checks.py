def run_dq_checks(spark, checks):
    """
    Runs a list of DQ checks and raises an exception if any fail.
    Each check is a dict with: query, operator, expected
    """
    for check in checks:
        query = check["query"]
        operator = check["operator"]
        expected = check["expected"]

        result = spark.sql(query).collect()[0][0]
        passed = eval(f"{result} {operator} {expected}")

        print(f"🔎 DQ Check: {query} -> {result} {operator} {expected} = {passed}")

        if not passed:
            raise ValueError(f"❌ DQ Check Failed: {query} returned {result}, expected {operator} {expected}")
