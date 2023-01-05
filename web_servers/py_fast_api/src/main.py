import logging

from src.db import db_module
from fastapi import APIRouter, Depends, FastAPI

from web_servers.py_fast_api.src.dependencies import get_db_session

logger = logging.getLogger("fastapi")


app = FastAPI(dependencies=[Depends(get_db_session)])

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(get_db_session)],
    responses={404: {"description": "Not found"}},
)


@app.get("/user/{user_id}/")
def get_user(user_id: int, db=Depends(get_db_session)):
    return db_module.UserRepo.get_user_by_id(db, user_id)


@app.get("/ping")
async def ping():
    return "pong"
