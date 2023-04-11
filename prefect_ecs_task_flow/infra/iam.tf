resource "aws_iam_policy" "ecs-task-execution-policy" {
  name = "prefectEcsTaskExecutionPolicy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:CreateTags",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetAuthorizationToken",
          "logs:CreateLogGroup",
          "logs:PutLogEvents",
          "ec2:DescribeSecurityGroups",
          "logs:CreateLogStream",
          "iam:PassRole",
          "ecs:RunTask",
          "ec2:DescribeNetworkInterfaces",
          "ssm:DescribeParameters",
          "ec2:DescribeVpcs",
          "ec2:CreateSecurityGroup",
          "ecs:RegisterTaskDefinition",
          "ec2:DeleteSecurityGroup",
          "ecr:BatchGetImage",
          "ec2:DescribeSubnets",
          "ecs:DescribeTasks",
          "ecr:BatchCheckLayerAvailability"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs-task-policy" {
  name = "prefectEcsTaskPolicy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
            "ec2:AuthorizeSecurityGroupIngress",
            "ecs:DescribeTaskDefinition",
            "ecs:DeregisterTaskDefinition",
            "logs:CreateLogStream",
            "ec2:DescribeNetworkInterfaces",
            "ecs:RunTask",
            "ec2:CreateSecurityGroup",
            "ecs:RegisterTaskDefinition",
            "logs:GetLogEvents",
            "ecs:StopTask",
            "ecs:DescribeTasks",
            "ecs:ListTaskDefinitions",
            "ecs:ListClusters",
            "logs:DescribeLogGroups",
            "ec2:CreateTags",
            "ecs:CreateCluster",
            "ecr:GetDownloadUrlForLayer",
            "ecs:DeleteCluster",
            "ecr:GetAuthorizationToken",
            "logs:PutLogEvents",
            "ec2:DescribeSecurityGroups",
            "ecs:DescribeClusters",
            "ecs:ListAccountSettings",
            "s3:PutObject",
            "s3:GetObject",
            "ec2:DescribeVpcs",
            "ec2:DeleteSecurityGroup",
            "ecr:BatchGetImage",
            "ec2:DescribeSubnets"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role" "prefect-ecs-task-execution-role" {
  name = "prefectEcsTaskExecutionRole"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {}
      }
    ]
  })
}

resource "aws_iam_role" "prefect-ecs-task-role" {
  name = "prefectEcsTaskRole"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {}
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ssm.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
       {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
    ]
  })
}



resource "aws_iam_role_policy_attachment" "ecs-task-execution-policy-attach" {
  role       = aws_iam_role.prefect-ecs-task-execution-role.name
  policy_arn = aws_iam_policy.ecs-task-execution-policy.arn
}

resource "aws_iam_role_policy_attachment" "ecs-task-policy-attach" {
  role       = aws_iam_role.prefect-ecs-task-role.name
  policy_arn = aws_iam_policy.ecs-task-policy.arn
}