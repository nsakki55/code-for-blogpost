import controlflow as cf


@cf.flow
def hello_flow(poem_topic: str):
    name = cf.Task("Get the user's name", user_access=True)
    poem = cf.Task(
        "Write a personalized poem about the provided topic",
        context=dict(name=name, topic=poem_topic),
    )
    return poem


print(hello_flow(poem_topic="AI"))
