import controlflow as cf
from typing import Optional
from pydantic import BaseModel


class Name(BaseModel):
    first: str
    last: Optional[str]


name_task = cf.Task("Get the user's name", result_type=Name, user_access=True)

print(name_task.run())
