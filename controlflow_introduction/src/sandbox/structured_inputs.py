import controlflow as cf
from pydantic import BaseModel


class UserPreferences(BaseModel):
    name: str
    age: int
    favorite_color: str


preferences_task = cf.Task(
    "Get user preferences",
    result_type=UserPreferences,
    user_access=True,
)

preferences = preferences_task.run()
print(f"Hello, {preferences.name}!")
