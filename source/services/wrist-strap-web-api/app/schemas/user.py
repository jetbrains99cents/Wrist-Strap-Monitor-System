# File: app/schemas/user.py

from pydantic import BaseModel
from typing import List

class User(BaseModel):
    email: str
    name: str
    roles: List[str]
    granted: bool