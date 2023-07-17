from prefect import flow
from prefect.deployments import run_deployment


@flow(name="Main Flow")
def main_flow():
    print("main flow")
    run_deployment(name="Sub Flow1/sub-flow1-deployment")
    run_deployment(name="Sub Flow2/sub-flow2-deployment")
    run_deployment(name="Sub Flow3/sub-flow3-deployment")


if __name__ == "__main__":
    main_flow()
