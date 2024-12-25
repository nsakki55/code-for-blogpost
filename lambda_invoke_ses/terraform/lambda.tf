resource "aws_ecr_repository" "invoke_ses" {
  name = "invoke-ses"
  image_tag_mutability = "MUTABLE"
}

resource "aws_lambda_function" "invoke_ses" {
  function_name = "invoke_ses"
  role          = aws_iam_role.lambda.arn
  architectures = ["x86_64"]
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.invoke_ses.repository_url}:latest"
  memory_size   = 512
  publish       = true
  timeout       = 10
  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.invoke_ses.id]
  }
}
