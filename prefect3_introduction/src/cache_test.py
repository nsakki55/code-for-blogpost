from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import INPUTS


@task(cache_policy=INPUTS, cache_expiration=timedelta(days=1))
def hello_task(name_input):
    # Doing some work
    print("Saying hello")
    return "hello " + name_input


@flow(log_prints=True)
def hello_flow(name_input):
    hello_task(name_input)
    hello_task(name_input)  # does not rerun


if __name__ == "__main__":
    hello_flow(name_input="test")
