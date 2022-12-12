import time
import boto3
import inspect
from locust import task
from botocore.config import Config
from locust import TaskSet, task, events 
from locust.contrib.fasthttp import FastHttpUser
from locust import task, events, constant 


def stopwatch(func):
    def wrapper(*args, **kwargs):
        previous_frame = inspect.currentframe().f_back
        _, _, task_name, task_func_name, _ = inspect.getframeinfo(previous_frame)
        task_func_name = task_func_name[0].split(".")[-1].split("(")[0]

        start = time.time()
        result = None

        try:
            result = func(*args, **kwargs)
            total = int((time.time() - start) * 1000)

        except Exception as e:
            events.request_failure.fire(
                request_type=task_name,
                name=task_func_name,
                response_time=total,
                response_length=len(result),
                exception=e,
            )
        else:
            events.request_success.fire(
                request_type=task_name,
                name=task_func_name,
                response_time=total,
                response_length=len(result),
            )
        return result

    return wrapper


class ProtocolClient:
    def __init__(self, host):
        self.endpoint_name = host.split("/")[-1]
        self.region = "ap-northeast-1"
        self.content_type = "application/json"
        self.payload = "0"

        boto3config = Config(retries={"max_attempts": 100, "mode": "standard"})
        self.sagemaker_client = boto3.client(
            "sagemaker-runtime", config=boto3config, region_name=self.region
        )

    @stopwatch
    def sagemaker_client_invoke_endpoint(self, instance_type: str):
        _endpoint_name = "{}-{}".format(
            self.endpoint_name, instance_type.replace(".", "")
        )
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=_endpoint_name,
            Body=self.payload,
            ContentType=self.content_type,
        )
        response_body = response["Body"].read()
        return response_body


class ProtocolLocust(FastHttpUser):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = ProtocolClient(self.host)
        self.client._locust_environment = self.environment


class ProtocolTasks(TaskSet):
    @task
    def mlt2medium(self):
        self.client.sagemaker_client_invoke_endpoint(instance_type="ml.t2.medium")

    @task
    def mlt2large(self):
        self.client.sagemaker_client_invoke_endpoint(instance_type="ml.t2.large")

    # @task
    # def mlt2xlarge(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.t2.xlarge")

    # @task
    # def mlt22xlarge(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.t2.2xlarge")

    # @task
    # def mlm5large(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.m5.large")

    # @task
    # def mlm5xlarge(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.m5.xlarge")

    # @task
    # def mlm52xlarge(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.m5.2xlarge")

    # @task
    # def mlm54xlarge(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.m5.4xlarge")

    # @task
    # def mlm512xlarge(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.m5.12xlarge")

    # @task
    # def mlm524large(self):
    #     self.client.sagemaker_client_invoke_endpoint(instance_type="ml.m5.24xlarge")


class ProtocolUser(ProtocolLocust):
    wait_time = constant(0)
    tasks = [ProtocolTasks]
