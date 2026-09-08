"""Optional Spark parity slice for accepted silver orders."""

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

root = Path(__file__).resolve().parents[1]
spark = SparkSession.builder.master("local[*]").appName("fieldforge-orders").getOrCreate()
orders = spark.read.parquet(str(root / "data/bronze/orders.parquet"))
accepted = orders.filter(
    F.col("currency").isin("USD", "CAD", "GBP")
    & ((F.col("delivered_at") == "") | (F.to_timestamp("delivered_at") >= F.to_timestamp("ordered_at")))
    & ((F.trim("customer_email") != "") | (F.trim("storefront_customer_id") != ""))
).withColumn("normalized_email", F.lower(F.trim("customer_email")))
expected = spark.read.parquet(str(root / "data/silver/orders.parquet"))
assert accepted.count() == expected.count()
assert set(accepted.select("order_id").toPandas().order_id) == set(expected.select("order_id").toPandas().order_id)
accepted.write.mode("overwrite").parquet(str(root / "artifacts/spark_orders"))
print(f"Spark parity passed: {accepted.count()} accepted orders")
spark.stop()
