from main_flow import main_flow
from prefect.deployments import Deployment
from prefect.filesystems import S3
from prefect_aws.ecs import ECSTask

ecs_task_block = ECSTask.load("ecs-task-block")
s3_block = S3.load("s3-block")

deployment = Deployment.build_from_flow(
    flow=main_flow,
    name="main-flow1-deployment",
    work_pool_name="ecs",
    infrastructure=ecs_task_block,
    storage=s3_block,
)

deployment.apply()
