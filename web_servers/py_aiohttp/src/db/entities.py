import datetime
import ujson
from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str
    email: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_archived: bool
    class Config:
        json_loads = ujson.loads

class UpdateUser(BaseModel):
    username: str
    email: str | None

    class Config:
        json_loads = ujson.loads