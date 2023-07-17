from prefect import flow

from sub_flow import sub_flow1, sub_flow2, sub_flow3


@flow(name="Main Flow", log_prints=True)
def main_flow():
    print("main flow")
    sub_flow1()
    sub_flow2()
    sub_flow3()


if __name__ == "__main__":
    main_flow()
