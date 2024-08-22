import controlflow as cf
from langchain_openai import ChatOpenAI


@cf.flow
def hello_flow(poem_topic: str):

    cf.default_model = ChatOpenAI(model="gpt-3.5-turbo")
    agent = cf.Agent("Marvin")
    name = cf.Task("Get the user's name", user_access=True)
    print(name)
    poem = cf.Task(
        "Write a personalized poem about the provided topic",
        context=dict(name=name, topic=poem_topic),
    )
    print(poem)
    return poem


hello_flow(poem_topic="AI")
