provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_s3_bucket" "data" {
  bucket_prefix = "schema-change-data-"
}

resource "aws_s3_bucket" "glue_job" {
  bucket_prefix = "glue-job-"
}

resource "aws_iam_role" "glue_job_role" {
  name = "glue_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = ""
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })

}

data "aws_iam_policy_document" "glue_job" {
  statement  {
      actions   = ["s3:*"]
      resources = ["*"]
    }
  statement {
      actions   = ["athena:*"]
      resources = ["*"]
    }
}

resource "aws_iam_policy" "glue_job" {
  name = "glue_job_policy"
  policy = data.aws_iam_policy_document.glue_job.json
}

resource "aws_iam_role_policy_attachment" "glue_job" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = aws_iam_policy.glue_job.arn
}

resource "aws_iam_role_policy_attachment" "glue_service_role_attachment" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_job" "update_iceberg_table_schema" {
  name              = "update_iceberg_table_schema"
  role_arn          = aws_iam_role.glue_job_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  max_retries       = 0
  execution_property {
    max_concurrent_runs = 10
  }

  command {
    script_location = "s3://${aws_s3_bucket.glue_job.bucket}/scripts/update_iceberg_table_schema.py"
  }

  default_arguments = {
    "--enable-glue-datacatalog"          = "true"
    "--TempDir"                          = "s3://${aws_s3_bucket.glue_job.bucket}/temporary/"
    "--spark-event-logs-path"            = "s3://${aws_s3_bucket.glue_job.bucket}/sparkHistoryLogs/"
    "--enable-job-insights"              = "false"
    "--enable-continuous-cloudwatch-log" = "true"
    "--datalake-formats"                 = "iceberg"
    # conf to enable iceberg format. ref: https://docs.aws.amazon.com/ja_jp/glue/latest/dg/aws-glue-programming-etl-format-iceberg.html
    "--conf" = "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions --conf spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog --conf spark.sql.catalog.glue_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO --conf spark.sql.catalog.glue_catalog.warehouse=file:///tmp/spark-warehouse --conf spark.sql.iceberg.check-ordering=false"
  }
}

resource "aws_glue_catalog_database" "test_database" {
  name         = "test_database"
  location_uri = "s3a://${aws_s3_bucket.data.bucket}/output/"
}