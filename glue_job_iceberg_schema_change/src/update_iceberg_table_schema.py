import sys
from typing import Dict

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext


S3_BUCKET = "schema-change-data-20241208085330834400000002"
TABLE_NAME = "test_table"
DATABASE_NAME = "test_database"
CATALOG_NAME = "glue_catalog"


def get_dynamic_frame_from_s3(glue_context: GlueContext, source_s3_path: str) -> DynamicFrame:
    print(f"Start get dynamic frame from S3. {source_s3_path=}")
    dyf = glue_context.create_dynamic_frame.from_options(
        format_options={
            "withHeader": True,
            "separator": ",",
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [source_s3_path],
        },
    )
    print(f"Finished get dynamic frame from S3. {dyf.count()=}")
    return dyf


def check_table_in_database(glue_context: GlueContext, database_name: str, table_name: str) -> bool:
    print(f"Start check table in database. {database_name=}, {table_name=}")
    tables = glue_context.spark_session.catalog.listTables(database_name)
    is_exist = table_name in [table.name for table in tables]
    print(f"Finished check table in database. {is_exist=}")
    return is_exist


def main(args: Dict[str, str]) -> None:
    sc = SparkContext()
    glue_context = GlueContext(sc)
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)
    print(f"Start update iceberg table schema. {args=}")

    dyf = get_dynamic_frame_from_s3(
        glue_context=glue_context,
        source_s3_path=f"s3://{S3_BUCKET}/input/{args['file_name']}",
    )
    df = dyf.toDF()
    df.printSchema()

    is_exist = check_table_in_database(glue_context=glue_context, database_name=DATABASE_NAME, table_name=TABLE_NAME)

    table_path = f"{CATALOG_NAME}.{DATABASE_NAME}.{TABLE_NAME}"
    if is_exist:
        sql = f"ALTER TABLE {table_path} SET TBLPROPERTIES ('write.spark.accept-any-schema' = 'true')"
        print(f"{sql=}")
        glue_context.spark_session.sql(sql)
        df.writeTo(table_path).option("mergeSchema","true").append()
    else:
        df.writeTo(table_path).tableProperty("format-version", "2").tableProperty("location", f"s3://{S3_BUCKET}/output").create()

    print(f"Finished update iceberg table schema. {args=}")
    job.commit()


if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ["JOB_NAME", "file_name"])
    main(args)
