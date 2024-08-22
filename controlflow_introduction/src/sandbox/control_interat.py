from controlflow import Flow, Task
import controlflow as cf
from langchain_openai import ChatOpenAI


title_task = Task("Generate a title for a poem about AI", result_type=str)
poem_task = Task(
    "Write a poem about AI using the provided title",
    result_type=str,
    context=dict(title=title_task),
)

with Flow():
    while poem_task.is_incomplete():
        poem_task.run_once()
    print(poem_task.result)
