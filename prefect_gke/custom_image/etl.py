from prefect import flow, get_run_logger, task

@task
def extract():
    logger = get_run_logger()
    logger.info("Extract Task")

@task
def transform():
    logger = get_run_logger()
    logger.info("Transform Task")

@task
def load():
    logger = get_run_logger()
    logger.info("Load Task")

@flow
def etl(name: str = "nsakki55"):
    logger = get_run_logger()
    logger.info(f"ETL Start by {name}")
    extract()
    transform()
    load()
    logger.info(f"ETL Finish")

if __name__ == "__main__":
    etl()
