import json
import logging

from fastapi import FastAPI, Request, Response
from src.db import db_module, entities

logger = logging.getLogger("fastapi")


app = FastAPI()


@app.get("/user/{user_id}/")
async def get_user(request: Request, user_id: int):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status_code=403, content='{description: "unauthorized"}')
    logger.info(f"getting user with id {user_id}")
    user = await db_module.UserAccessModel.get_user_by_id(request.app.state.db, user_id)
    if user:
        return Response(status_code=200, content=user.json())
    return Response(status_code=404, content='{"description": "user not found"}')


@app.patch("/user/{user_id}/")
async def update_user(request: Request, user_id: int, data: entities.UpdateUser):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status_code=403, content='{description: "unauthorized"}')
    logger.info(f"try to update with id {user_id}")
    user = await db_module.UserAccessModel.update_user(request.app.state.db, user_id, data)
    if user:
        return Response(status_code=200, content=user.json())
    return Response(status_code=404, content='{"description": "user not found"}')


@app.get("/to_json/")
async def to_json(request: Request, param1: str, param2: str, param3: str):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status_code=403, content='{description: "unauthorized"}')
    return Response(status_code=200, content=json.dumps({"param1": param1, "param2": param2, "param3": param3}))


@app.get("/plain/")
async def plain(request: Request, param1: str, param2: str, param3: str):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status_code=403, content='{description: "unauthorized"}')
    return Response(status_code=200, content=f"{param1=}, {param2=}, {param3=}")


@app.get("/ping")
async def ping():
    return "pong"


@app.on_event("startup")
async def startup():
    from src import settings
    
    app.state.db = await db_module.create_session(settings.DATABASE_URI)


@app.on_event("shutdown")
async def shutdown():
    await db_module.close_session(app.state.db)

