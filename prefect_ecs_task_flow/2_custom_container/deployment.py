from my_flow import etl_flow
from prefect.deployments import Deployment
from prefect_aws.ecs import ECSTask

ecs_task_block = ECSTask.load("custom-container-ecs-task-block")

deployment = Deployment.build_from_flow(
    flow=etl_flow,
    name="custom-container-deployment",
    work_pool_name="ecs-pool",
    infrastructure=ecs_task_block,
)

deployment.apply()
