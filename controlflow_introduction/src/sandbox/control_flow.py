from controlflow import Flow, Task, flow


@flow
def conditional_flow():
    coin_toss_task = Task("Flip a coin", result_type=["heads", "tails"])
    # manually run the coin-toss task
    outcome = coin_toss_task.run()

    # generate a different task based on the outcome of the toss
    if outcome == "heads":
        poem = Task("Write a poem about Mt. Rushmore", result_type=str)
    elif outcome == "tails":
        poem = Task("Write a poem about the Grand Canyon", result_type=str)

    # return the poem task
    return poem


print(conditional_flow())
# Upon granite heights, 'neath skies of blue,
# Mount Rushmore stands, a sight to view.
# ...
