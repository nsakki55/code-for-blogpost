import time

from prefect import flow, task


@task()
def a():
    print("task A")
    time.sleep(5)


@task()
def b():
    print("task B")
    time.sleep(5)


@task()
def c():
    print("task C")
    time.sleep(5)


@flow(name="Sub Flow1", log_prints=True)
def sub_flow1():
    print("sub flow1")
    a()
    b()


@flow(name="Sub Flow2", log_prints=True)
def sub_flow2():
    print("sub flow2")
    b()
    c()


@flow(name="Sub Flow3", log_prints=True)
def sub_flow3():
    print("sub flow3")
    a()
    c()


if __name__ == "__main__":
    sub_flow1()
    sub_flow2()
    sub_flow3()
