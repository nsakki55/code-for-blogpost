import sys
from typing import Dict

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext

from pyspark.sql import DataFrame

S3_ENDPOINT_URL = "http://s3.dev:4566"
S3_BUCKET = "test-job-bucket"
TABLE_NAME = "test_table"
DATABASE_NAME = "test_database"


def get_dynamic_frame_from_s3(glue_context: GlueContext, source_s3_path: str) -> DynamicFrame:
    dyf = glue_context.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": '"',
            "withHeader": True,
            "separator": ",",
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [source_s3_path],
            "recurse": True,
        },
    )
    return dyf


def dynamic_frame_to_dataframe(dyf: DynamicFrame) -> DataFrame:
    return dyf.toDF()


def check_table_in_database(glue_context: GlueContext, database_name: str, table_name: str) -> bool:
    tables_collection = glue_context.spark_session.catalog.listTables(database_name)
    return table_name in [table.name for table in tables_collection]


def append_iceberg_table(df: DataFrame, table_name: str, table_location) -> None:
    df.writeTo(table_name).tableProperty("format-version", "2").tableProperty("location", table_location).append()


def create_iceberg_table(df: DataFrame, table_name: str, table_location) -> None:
    df.writeTo(table_name).tableProperty("format-version", "2").tableProperty("location", table_location).create()


def main(args: Dict[str, str]) -> None:
    sc = SparkContext()
    glue_context = GlueContext(sc)

    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    dyf = get_dynamic_frame_from_s3(glue_context=glue_context, source_s3_path=f"s3://{S3_BUCKET}/input")
    df = dynamic_frame_to_dataframe(dyf=dyf)
    is_exist = check_table_in_database(glue_context=glue_context, database_name=DATABASE_NAME, table_name=TABLE_NAME)
    if is_exist:
        append_iceberg_table(df, TABLE_NAME, f"s3://{S3_BUCKET}/output")
    else:
        create_iceberg_table(df, TABLE_NAME, f"s3://{S3_BUCKET}/output")

    job.commit()


if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ["JOB_NAME"])
    main(args)
