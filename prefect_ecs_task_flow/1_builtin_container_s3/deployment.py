from my_flow import etl_flow
from prefect.deployments import Deployment
from prefect_aws.ecs import ECSTask
from prefect.filesystems import S3

s3_block = S3.load("etl-s3-block")
ecs_task_block = ECSTask.load("builtin-container-ecs-task-block")

deployment = Deployment.build_from_flow(
    flow=etl_flow,
    name="builtin-container-s3-deployment",
    work_pool_name="ecs-pool",
    storage=s3_block,
    infrastructure=ecs_task_block,
)

deployment.apply()
