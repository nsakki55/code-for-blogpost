from prefect_aws.ecs import ECSTask

ecs = ECSTask(
    image="*****.dkr.ecr.ap-northeast-1.amazonaws.com/prefect-custom-container:latest",
    cluster="arn:aws:ecs:ap-northeast-1:*****:cluster/prefect-ecs",
    cpu="256",
    memory="512",
    stream_output=True,
    configure_cloudwatch_logs=True,
    execution_role_arn="arn:aws:iam::*****:role/prefectEcsTaskExecutionRole",
    task_role_arn="arn:aws:iam::*****:role/prefectEcsTaskRole",
    vpc_id="vpc-******",
    task_customizations=[
  {
    "op": "replace",
    "path": "/networkConfiguration/awsvpcConfiguration/assignPublicIp",
    "value": "DISABLED"
  },
  {
    "op": "add",
    "path": "/networkConfiguration/awsvpcConfiguration/subnets",
    "value": [
      "subnet-******"
    ]
  }
]
)
ecs.save("custom-container-ecs-task-block", overwrite=True)