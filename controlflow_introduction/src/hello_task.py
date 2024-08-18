import controlflow as cf
from pydantic import BaseModel


class Name(BaseModel):
    first: str
    last: str


@cf.flow
def run_flow():
    name = cf.Task("Get the user's name", user_access=True, result_type=Name)
    poem = cf.Task("Write a personalized poem", context=dict(name=name))


run_flow()
