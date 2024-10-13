import io
import csv
import boto3
import os
import shutil
import pytest

from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import DataFrame
from pyspark.sql.types import Row
from pyspark.sql.functions import col
from awsglue.context import GlueContext
from pyspark.sql import SparkSession

from src.glue_job import get_dynamic_frame_from_s3, append_iceberg_table, create_iceberg_table

# AWS Configuration for localstack defined by compose.yaml
S3_ENDPOINT_URL = "http://s3.dev:4566"
AWS_REGION = "ap-northeast-1"
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"

# Warehouse path for local iceberg table
WAREHOUSE_PATH = "./spark-warehouse"


@pytest.fixture(scope="session")
def glue_context() -> GlueContext:
    spark = (
        SparkSession.builder.master("local[1]")
        # Configure for testing fast
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.dagGraph.retainedRootRDD", "1")
        .config("spark.ui.retainedJobs", "1")
        .config("spark.ui.retainedStages", "1")
        .config("spark.ui.retainedTasks", "1")
        .config("spark.sql. ui.retainedExecutions", "1")
        .config("spark.worker.ui.retainedExecutors", "1")
        .config("spark.worker.ui.retainedDrivers", "1")
        # Configure for testing iceberg table operation
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", WAREHOUSE_PATH)
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.3.0")
        .config("spark.sql.catalog.local.default.write.metadata-flush-after-create", "true")
        .config("spark.sql.defaultCatalog", "local")
        # Configure for testing local hive metastore
        .config("spark.sql.hive.metastore.jars", "builtin")
        .config("spark.sql.hive.metastore.version", "2.3.9")
        .config("spark.sql.catalogImplementation", "in-memory")
        .getOrCreate()
    )
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", S3_ENDPOINT_URL)
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint.region", AWS_REGION)
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.change.detection.mode", "None")
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.change.detection.version.required", "false")

    yield GlueContext(spark.sparkContext)
    spark.stop()


@pytest.fixture(scope="session")
def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


@pytest.fixture(scope="session")
def s3_bucket(s3_client: boto3.client) -> str:
    bucket_name = "test-s3-bucket"

    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except Exception:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )

    yield bucket_name

    try:
        s3_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Failed to clean up test bucket: {e}")


@pytest.fixture(scope="session")
def setup_s3_data(s3_client: boto3.client, s3_bucket: str) -> dict[str, str]:
    key = "test_data.csv"
    inputs = [
        {"col1": "val1", "col2": 1, "col3": "2000/01/01 01:00:00"},
        {"col1": "val2", "col2": 2, "col3": "2000/01/02 02:00:00"},
        {"col1": "val3", "col2": 3, "col3": "2000/01/03 03:00:00"},
    ]
    input_str = io.StringIO()
    w = csv.DictWriter(input_str, fieldnames=inputs[0].keys())
    w.writeheader()
    for input in inputs:
        w.writerow(input)

    body = input_str.getvalue()
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=body)

    yield {"bucket_name": s3_bucket, "key": key}

    try:
        s3_client.delete_object(Bucket=s3_bucket, Key=key)
    except Exception as e:
        print(f"Failed to clean up test data: {e}")


def test_get_dynamic_frame_from_s3(glue_context: GlueContext, setup_s3_data: dict[str, str]) -> None:
    source_s3_path = f"s3://{setup_s3_data['bucket_name']}/{setup_s3_data['key']}"
    result = get_dynamic_frame_from_s3(glue_context=glue_context, source_s3_path=source_s3_path)

    assert isinstance(result, DynamicFrame)
    assert result.count() == 3

    df = result.toDF()
    assert len(df.columns) == 3
    assert df.columns == ["col1", "col2", "col3"]

    rows = df.collect()
    assert rows == [
        Row(col1="val1", col2="1", col3="2000/01/01 01:00:00"),
        Row(col1="val2", col2="2", col3="2000/01/02 02:00:00"),
        Row(col1="val3", col2="3", col3="2000/01/03 03:00:00"),
    ]


@pytest.fixture(scope="module")
def sample_dataframe(glue_context: GlueContext) -> DataFrame:
    spark = glue_context.spark_session
    df = spark.createDataFrame(
        [
            ("val1", 1, "2000/01/01 01:00:00"),
            ("val2", 2, "2000/01/02 02:00:00"),
            ("val3", 3, "2000/01/03 03:00:00"),
        ],
        ["col1", "col2", "col3"],
    )
    return df


@pytest.fixture(scope="session")
def cleanup_warehouse() -> None:
    yield
    if os.path.exists(WAREHOUSE_PATH):
        shutil.rmtree(WAREHOUSE_PATH)


@pytest.fixture(scope="module")
def test_table(glue_context: GlueContext, sample_dataframe: DataFrame) -> str:
    spark = glue_context.spark_session
    table_name = "test_table"
    database_name = "default"
    try:
        sample_dataframe.writeTo(f"local.{table_name}").create()
        # sample_dataframe.writeTo(f"local.{database_name}.{table_name}").create()
        yield table_name
    finally:
        spark.sql(f"DROP TABLE IF EXISTS local.{table_name}")


def test_create_iceberg_table(glue_context: GlueContext, cleanup_warehouse: None, sample_dataframe: DataFrame) -> None:
    spark = glue_context.spark_session

    # new table setting
    table_name = "test_new_table"
    table_full_name = f"local.{table_name}"
    table_location = f"{WAREHOUSE_PATH}/{table_name}"

    create_iceberg_table(df=sample_dataframe, table_name=table_full_name, table_location=table_location)

    result_df = spark.table(table_full_name)
    assert result_df.collect() == sample_dataframe.collect()


def test_append_iceberg_table(
    glue_context: GlueContext, cleanup_warehouse: None, sample_dataframe: DataFrame, test_table: str
) -> None:
    spark = glue_context.spark_session

    # existing table setting
    table_full_name = f"local.{test_table}"
    table_location = f"{WAREHOUSE_PATH}/{test_table}"

    # append dataframe
    append_data = [
        ("val4", 4, "2000/01/04 04:00:00"),
        ("val5", 5, "2000/01/05 05:00:00"),
    ]
    append_df = spark.createDataFrame(append_data, sample_dataframe.schema)

    spark.catalog.setCurrentDatabase("default")

    append_iceberg_table(df=append_df, table_name=table_full_name, table_location=table_location)

    result_df = spark.table(table_full_name)
    new_df = result_df.filter(~col("col1").isin(["val1", "val2", "val3"]))
    assert new_df.collect() == append_df.collect()
    assert result_df.count() == 5
