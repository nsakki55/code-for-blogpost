import gevent
from locust import HttpUser, task
from locust.env import Environment
from locust.stats import StatsCSVFileWriter


class ELBUser(HttpUser):
    host = "http://alb-app-1499646873.ap-northeast-1.elb.amazonaws.com"

    @task
    def test_request(self):
        self.client.get("/test")


env: Environment = Environment(user_classes=[ELBUser])

csv_writer: StatsCSVFileWriter = StatsCSVFileWriter(
    environment=env,
    base_filepath="./alb",
    full_history=True,
    percentiles_to_report=[0.0, 100.0],
)
gevent.spawn(csv_writer)

env.create_local_runner()
env.runner.start(1, spawn_rate=1)

gevent.spawn_later(60, lambda: env.runner.quit())
env.runner.greenlet.join()
