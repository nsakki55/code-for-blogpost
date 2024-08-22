import controlflow as cf
import random


def roll_die() -> int:
    """Roll a 6-sided diee."""
    return random.randint(1, 6)


task = cf.Task(
    objective="Roll a die, then roll again as many times as the first value",
    instructions="Report the history of rolls",
    tools=[roll_die],
)
task.run()
