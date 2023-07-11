import ujson
import logging

import asyncio
import uvloop
from aiohttp.web import Application, Request, Response, run_app
from src.db import db_module, entities

logger = logging.getLogger("aiohttp")


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def get_user(request: Request):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status=403, body='{description: "unauthorized"}')
    user_id = int(request.match_info["user_id"])
    logger.info(f"getting user with id {user_id}")
    user = await db_module.UserAccessModel.get_user_by_id(request.app.db, user_id)
    if user:
        return Response(status=200, body=user.json())
    return Response(status=404, body='{"description": "user not found"}')


async def update_user(request: Request):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status=403, body='{description: "unauthorized"}')
    user_id = int(request.match_info["user_id"])
    body = await request.json()
    data = entities.UpdateUser(**body)
    logger.info(f"try to update with id {user_id}")
    user = await db_module.UserAccessModel.update_user(request.app.db, user_id, data)
    if user:
        return Response(status=200, body=user.json())
    return Response(status=404, body='{"description": "user not found"}')


async def to_json(request: Request):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status=403, body='{description: "unauthorized"}')
    param1 = request.query.get("param1")
    param2 = request.query.get("param2")
    param3 = request.query.get("param3")
    return Response(status=200, body=ujson.dumps({"param1": param1, "param2": param2, "param3": param3}))


async def plain(request: Request):
    if request.headers.get("token") != "hardcoded_token":
        return Response(status=403, body='{description: "unauthorized"}')
    param1 = request.query.get("param1")
    param2 = request.query.get("param2")
    param3 = request.query.get("param3")
    return Response(status=200, body=f"{param1=}, {param2=}, {param3=}")


async def ping(_: Request):
    return Response(body="pong")


async def on_startup(app):
    from src import settings

    app.db = await db_module.create_session(settings.DATABASE_URI)


async def on_cleanup(app):
    await db_module.close_session(app.db)


def register_routers(app):

    app.router.add_get("/ping", ping)
    app.router.add_get("/plain/", plain)
    app.router.add_get("/to_json/", to_json)
    app.router.add_get("/user/{user_id}/", get_user)
    app.router.add_patch("/user/{user_id}/", update_user)


async def app():
    app = Application()

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)
    logger.info("Service started")
    return app


if __name__ == "__main__":
    run_app(app(), port=8000)
