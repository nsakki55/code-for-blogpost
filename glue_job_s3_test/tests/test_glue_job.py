import pytest
import boto3
import io
import csv

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import Row

from src.glue_job import get_dynamic_frame_from_s3, write_dynamic_frame_to_s3

# AWS Configuration for localstack defined by compose.yaml
S3_ENDPOINT_URL = "http://s3.dev:4566"
AWS_REGION = "ap-northeast-1"
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"


@pytest.fixture(scope="session")
def glue_context() -> GlueContext:
    spark = (
        SparkSession.builder.master("local[1]")
        # Configure for testing fast
        # https://kakehashi-dev.hatenablog.com/entry/2023/07/13/110000
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
        .getOrCreate()
    )
    # Configuration for localstack
    # https://future-architect.github.io/articles/20220428a
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


# https://docs.pytest.org/en/6.2.x/fixture.html#factories-as-fixtures
@pytest.fixture
def get_s3_objects(s3_client):
    def _get_s3_objects(s3_bucket: str, prefix: str) -> list[str] | None:
        try:
            response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
        except Exception:
            return

    return _get_s3_objects


@pytest.fixture(scope="module")
def sample_dynamicframe(glue_context: GlueContext) -> DynamicFrame:
    spark = glue_context.spark_session
    df = spark.createDataFrame(
        [
            ("val1", 1, "2000/01/01 01:00:00"),
            ("val2", 2, "2000/01/02 02:00:00"),
            ("val3", 3, "2000/01/03 03:00:00"),
        ],
        ["col1", "col2", "col3"],
    )
    dyf = DynamicFrame.fromDF(df, glue_context, "dyf")

    return dyf


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


def test_write_dynamic_frame_from_s3(
    glue_context: GlueContext,
    s3_bucket,
    sample_dynamicframe: DynamicFrame,
    get_s3_objects,
) -> None:
    file_key = "test_write_data"
    destination_s3_path = f"s3://{s3_bucket}/{file_key}"
    write_dynamic_frame_to_s3(
        glue_context=glue_context,
        dyf=sample_dynamicframe,
        destination_s3_path=destination_s3_path,
    )
    actual_s3_objects = get_s3_objects(s3_bucket=s3_bucket, prefix=file_key)

    assert len(actual_s3_objects) > 0
    assert any([object for object in actual_s3_objects if object.endswith(".parquet")])
