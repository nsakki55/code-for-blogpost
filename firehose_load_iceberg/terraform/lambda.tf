resource "aws_cloudwatch_log_group" "firehose_processor_lambda" {
  name              = "/aws/lambda/firehose-processor"
  retention_in_days = 365
}

resource "aws_iam_role" "firehose_processor_lambda" {
  name = "firehose_processor_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "firehose_processor_lambda" {
  name        = "firehose_processor_lambda_policy"
  description = "Policy for Firehose processor Lambda role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${local.aws_region}:${local.aws_account_id}:log-group:${aws_cloudwatch_log_group.firehose_processor_lambda.name}:*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "firehose_processor_lambda" {
  role       = aws_iam_role.firehose_processor_lambda.name
  policy_arn = aws_iam_policy.firehose_processor_lambda.arn
}

data "archive_file" "firehose_processor_lambda" {
  type        = "zip"
  source_dir  = "../lambda/"
  output_path = "../lambda/firehose_processor.zip"
}

resource "aws_lambda_function" "firehose_processor_lambda" {
  function_name    = "firehose-processor-handler"
  role             = aws_iam_role.firehose_processor_lambda.arn
  filename         = data.archive_file.firehose_processor_lambda.output_path
  handler          = "firehose_processor.lambda_handler"
  runtime          = "python3.12"
  timeout          = 70
  source_code_hash = filebase64sha256(data.archive_file.firehose_processor_lambda.output_path)

  logging_config {
    log_group  = aws_cloudwatch_log_group.firehose_processor_lambda.name
    log_format = "Text"
  }

  depends_on = [
    aws_cloudwatch_log_group.firehose_processor_lambda,
    data.archive_file.firehose_processor_lambda,
  ]
}

resource "aws_lambda_alias" "firehose_processor_lambda_default" {
  name             = "default"
  description      = "Default version."
  function_name    = aws_lambda_function.firehose_processor_lambda.arn
  function_version = "1"
  lifecycle {
    ignore_changes = [function_version]
  }
}
