from datetime import datetime

from prefect import flow, get_run_logger


@flow(flow_run_name="my-flow-{date}")
def my_flow(date: datetime = None):
    logger = get_run_logger()
    logger.info(f"date: {date}")


if __name__ == "__main__":
    now = datetime.now()
    my_flow(date=now)
