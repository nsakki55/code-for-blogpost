resource "aws_iam_role" "lambda" {
  name               = "lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda.json
}

data "aws_iam_policy_document" "lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail"
    ]
    resources = [aws_ses_domain_identity.ses_smtp.arn]
  }
  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [aws_secretsmanager_secret.smtp_credential.arn]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "lambda_policy"
  policy = data.aws_iam_policy_document.lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}


