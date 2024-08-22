import controlflow as cf
from langchain_anthropic import ChatAnthropic
import random

model = ChatAnthropic(model="claude-3-opus-20240229")
agent = cf.Agent(model=model)


# this function will be used as a tool by task 2
def roll_dice(n: int) -> int:
    """Roll n dice"""
    return [random.randint(1, 6) for _ in range(n)]


@cf.flow
def dice_flow():

    # task 1: ask the user how many dice to roll
    user_task = cf.Task(
        "Ask the user how many dice to roll", result_type=int, user_access=True
    )

    # task 2: roll the dice
    dice_task = cf.Task(
        "Roll the dice",
        context=dict(n=user_task),
        tools=[roll_dice],
        result_type=list[int],
    )

    return dice_task


result = dice_flow()
print(f"The result is: {result}")
