import asyncio
from datetime import datetime

import prefect
from prefect import flow, task


@task(name="set flow run name task")
async def set_flow_run_name(name: str) -> None:
    """Set user specify flow run name."""
    task_run_context = prefect.context.get_run_context()
    flow_run_id = task_run_context.task_run.flow_run_id

    async with prefect.get_client() as client:
        await client.update_flow_run(flow_run_id=flow_run_id, name=name)


@flow()
async def my_flow():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    flow_name = f"my-flow-{now}"
    await set_flow_run_name(name=flow_name)


if __name__ == "__main__":
    asyncio.run(my_flow())
