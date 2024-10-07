import sys
from typing import Dict

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext

S3_ENDPOINT_URL = "http://s3.dev:4566"
AWS_REGION = "ap-northeast-1"
S3_BUCKET = "test-job-bucket"


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


def write_dynamic_frame_to_s3(glue_context: GlueContext, dyf: DynamicFrame, destination_s3_path: str) -> None:
    glue_context.write_dynamic_frame.from_options(
        frame=dyf,
        connection_type="s3",
        connection_options={"path": destination_s3_path},
        format="parquet",
        format_options={"writeHeader": True},
    )


def main(args: Dict[str, str]) -> None:
    sc = SparkContext()
    if args["JOB_NAME"] == "test":
        sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", S3_ENDPOINT_URL)
        sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint.region", AWS_REGION)
        sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    glue_context = GlueContext(sc)

    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    dyf = get_dynamic_frame_from_s3(glue_context=glue_context, source_s3_path=f"s3://{S3_BUCKET}/test_data.csv")
    write_dynamic_frame_to_s3(glue_context=glue_context, dyf=dyf, destination_s3_path=f"s3://{S3_BUCKET}/output")

    job.commit()


if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ["JOB_NAME"])
    main(args)
