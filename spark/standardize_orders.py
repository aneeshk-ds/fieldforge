"""Optional Spark parity slice for accepted silver orders."""

from datetime import UTC, datetime

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from fieldforge.settings import artifacts_root, bronze_dir, silver_dir
from fieldforge.utils import write_json

spark = SparkSession.builder.master("local[*]").appName("fieldforge-orders").getOrCreate()
orders = spark.read.parquet(str(bronze_dir() / "orders.parquet"))
accepted = orders.filter(
    F.col("currency").isin("USD", "CAD", "GBP")
    & ((F.col("delivered_at") == "") | (F.to_timestamp("delivered_at") >= F.to_timestamp("ordered_at")))
    & ((F.trim("customer_email") != "") | (F.trim("storefront_customer_id") != ""))
).withColumn("normalized_email", F.lower(F.trim("customer_email")))
expected = spark.read.parquet(str(silver_dir() / "orders.parquet"))
accepted_ids = accepted.select("order_id")
expected_ids = expected.select("order_id")
accepted_count = accepted_ids.count()
expected_count = expected_ids.count()
missing_count = expected_ids.join(accepted_ids, "order_id", "left_anti").count()
unexpected_count = accepted_ids.join(expected_ids, "order_id", "left_anti").count()
assert accepted_count == expected_count
assert missing_count == 0
assert unexpected_count == 0
accepted.write.mode("overwrite").parquet(str(artifacts_root() / "spark_orders"))
write_json(
    artifacts_root() / "spark_parity.json",
    {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "pyspark_version": pyspark.__version__,
        "java_version": spark.sparkContext._jvm.java.lang.System.getProperty("java.version"),
        "accepted_orders": accepted_count,
        "expected_orders": expected_count,
        "missing_order_ids": missing_count,
        "unexpected_order_ids": unexpected_count,
        "status": "passed",
    },
)
print(f"Spark parity passed: {accepted_count} accepted orders; 0 ID differences")
spark.stop()
