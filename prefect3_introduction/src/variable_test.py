from prefect.variables import Variable
from prefect import task, flow


@task
def get_variable():
    var = Variable.get("test4")
    print(var)
    print(var["result"])
    print(var["result"][0])
    print(type(var["result"][0]))

    print(var["time"])
    print(type(var["time"]))


@flow
def main():
    get_variable()


if __name__ == "__main__":
    main()
