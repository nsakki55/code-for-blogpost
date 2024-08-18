from prefect import flow, task
import asyncio

@task
async def fetch_user_data(user_id):
    return {"id": user_id, "score": user_id * 10}

@task
def calculate_average(user_data):
    return sum(user["score"] for user in user_data) / len(user_data)

@flow
async def prefect_2_flow(n_users: int = 10):  # ❌
    # users = await fetch_user_data.map(range(1, n_users + 1))
    users = fetch_user_data.map(range(1, n_users + 1))
    avg = calculate_average.submit(users)
    print(f"Users: {users.result()}")
    print(f"Average score: {avg.result()}")

@flow
def prefect_3_flow(n_users: int = 10):  # ✅
    users = fetch_user_data.map(range(1, n_users + 1))
    avg = calculate_average.submit(users)
    print(f"Users: {users.result()}")
    print(f"Average score: {avg.result()}")

try:
    asyncio.run(prefect_2_flow())
    raise AssertionError("Expected a TypeError")
except TypeError as e:
    assert "can't be used in 'await' expression" in str(e)

prefect_3_flow()
