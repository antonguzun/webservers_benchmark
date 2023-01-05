import logging

from fastapi import APIRouter, FastAPI, Request, Response
from src.db import db_module

logger = logging.getLogger("fastapi")


app = FastAPI()

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@app.get("/user/{user_id}/")
async def get_user(request: Request, user_id: int):
    logger.info(f"getting user with id {user_id}")
    user = await db_module.UserRepo.get_user_by_id(request.app.state.db, user_id)
    if user:
        return Response(status_code=200, content=user.json())
    return Response(status_code=404, content='{"description": "user not found"}')


@app.get("/ping")
async def ping():
    return "pong"


@app.on_event("startup")
async def startup():
    from src import settings

    app.state.db = await db_module.create_session(settings.DATABASE_URI)


@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
