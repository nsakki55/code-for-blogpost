resource "aws_cloudwatch_log_group" "firehose_load_iceberg" {
  name              = "/aws/firehose/firehose-load-iceberg"
  retention_in_days = 365
}

resource "aws_cloudwatch_log_stream" "firehose_load_iceberg" {
  name           = "firehose-load-iceberg-log-stream"
  log_group_name = aws_cloudwatch_log_group.firehose_load_iceberg.name
}

resource "aws_iam_role" "firehose_load_iceberg" {
  name = "firehose_load_iceberg_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "firehose.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "firehose_load_iceberg" {
  name        = "firehose_load_iceberg_policy"
  description = "Policy for Firehose load iceberg role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::*",
          "arn:aws:s3:::*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.aws_region}:${local.aws_account_id}:log-group:${aws_cloudwatch_log_group.firehose_load_iceberg.name}:*",
          aws_cloudwatch_log_stream.firehose_load_iceberg.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetTable",
          "glue:GetDatabase",
          "glue:UpdateTable"
        ]
        Resource = [
          "arn:aws:glue:*:*:catalog",
          "arn:aws:glue:*:*:database/*",
          "arn:aws:glue:*:*:table/*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards"
        ]
        Resource = [
          "arn:aws:kinesis:*:*:stream/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunctionConfiguration"
        ]
        Resource = [
          "arn:aws:lambda:*:*:function:*:*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "firehose_load_iceberg" {
  role       = aws_iam_role.firehose_load_iceberg.name
  policy_arn = aws_iam_policy.firehose_load_iceberg.arn
}

resource "aws_s3_bucket" "firehose_load_iceberg" {
  bucket_prefix = "firehose-load-iceberg-"
}

resource "aws_kinesis_firehose_delivery_stream" "firehose_load_iceberg" {
  name        = "firehose-load-iceberg"
  destination = "iceberg"

  iceberg_configuration {
    role_arn           = aws_iam_role.firehose_load_iceberg.arn
    catalog_arn        = "arn:aws:glue:${local.aws_region}:${local.aws_account_id}:catalog"
    buffering_size     = 5
    buffering_interval = 10

    s3_configuration {
      role_arn   = aws_iam_role.firehose_load_iceberg.arn
      bucket_arn = aws_s3_bucket.firehose_load_iceberg.arn
    }

    processing_configuration {
      enabled = "true"

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${aws_lambda_function.firehose_processor_lambda.arn}:${aws_lambda_alias.firehose_processor_lambda_default.name}"
        }
        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = 10
        }
      }
    }

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_load_iceberg.name
      log_stream_name = aws_cloudwatch_log_stream.firehose_load_iceberg.name
    }
  }
}
