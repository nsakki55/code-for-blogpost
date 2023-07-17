from prefect.deployments import Deployment
from prefect.filesystems import S3
from prefect_aws.ecs import ECSTask

from sub_flow import sub_flow1, sub_flow2, sub_flow3

ecs_task_block = ECSTask.load("ecs-task-block")
s3_block = S3.load("s3-block")

deployment_sub_flow1 = Deployment.build_from_flow(
    flow=sub_flow1,
    name="sub-flow1-deployment",
    work_pool_name="ecs",
    infrastructure=ecs_task_block,
    storage=s3_block,
    infra_overrides={"cpu": 512, "memory": 1024},
)

deployment_sub_flow1.apply()

deployment_sub_flow2 = Deployment.build_from_flow(
    flow=sub_flow2,
    name="sub-flow2-deployment",
    work_pool_name="ecs",
    infrastructure=ecs_task_block,
    storage=s3_block,
    infra_overrides={"cpu": 1024, "memory": 2048},
)

deployment_sub_flow2.apply()

deployment_sub_flow3 = Deployment.build_from_flow(
    flow=sub_flow3,
    name="sub-flow3-deployment",
    work_pool_name="ecs",
    infrastructure=ecs_task_block,
    storage=s3_block,
    infra_overrides={"cpu": 2048, "memory": 4096},
)

deployment_sub_flow3.apply()
