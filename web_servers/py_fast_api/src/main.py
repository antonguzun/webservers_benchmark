import logging

from fastapi import APIRouter, Depends, FastAPI, Response
from src.db import db_module
from src.dependencies import get_db_session

logger = logging.getLogger("fastapi")


app = FastAPI(dependencies=[Depends(get_db_session)])
app = FastAPI()
router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@app.get("/user/{user_id}/")
async def get_user(user_id: int, db=Depends(get_db_session)):
    user = await db_module.UserRepo.get_user_by_id(db, user_id)
    if not user:
        return Response(status_code=404, content='{"error": "user not found"}')
    return Response(status_code=200, content=user.json())


@app.get("/ping")
async def ping():
    return "pong"
