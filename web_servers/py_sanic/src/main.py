import json
import logging

from sanic import Request, Sanic, json, text
from src.db import db_module, entities

logger = logging.getLogger("aiohttp")


async def get_user(request: Request, user_id: int):
    if request.headers.get("token") != "hardcoded_token":
        return json(status=403, body='{description: "unauthorized"}')
    logger.info(f"getting user with id {user_id}")
    user = await db_module.UserAccessModel.get_user_by_id(request.app.ctx.db, user_id)
    if user:
        return json(status=200, body=user.json())
    return json(status=404, body='{"description": "user not found"}')


async def update_user(request: Request, user_id: int):
    if request.headers.get("token") != "hardcoded_token":
        return json(status=403, body='{description: "unauthorized"}')
    data = entities.UpdateUser(**request.json)
    logger.info(f"try to update with id {user_id}")
    user = await db_module.UserAccessModel.update_user(
        request.app.ctx.db, user_id, data
    )
    if user:
        return json(status=200, body=user.json())
    return json(status=404, body='{"description": "user not found"}')


async def to_json(request: Request):
    if request.headers.get("token") != "hardcoded_token":
        return json(status=403, body='{description: "unauthorized"}')
    param1 = request.args.get("param1")
    param2 = request.args.get("param2")
    param3 = request.args.get("param3")
    return json(status=200, body={"param1": param1, "param2": param2, "param3": param3})


async def plain(request: Request):
    if request.headers.get("token") != "hardcoded_token":
        return json(status=403, body='{description: "unauthorized"}')
    param1 = request.args.get("param1")
    param2 = request.args.get("param2")
    param3 = request.args.get("param3")
    return text(status=200, body=f"{param1=}, {param2=}, {param3=}")


async def ping(_: Request):
    return json(body="pong")


async def on_startup(app):
    from src import settings

    app.ctx.db = await db_module.create_session(settings.DATABASE_URI)


async def on_cleanup(app):
    await db_module.close_session(app.ctx.db)


def register_routers(app):
    app.add_route(ping, "/ping/", methods=["GET"])
    app.add_route(to_json, "/to_json/", methods=["GET"])
    app.add_route(plain, "/plain/", methods=["GET"])
    app.add_route(get_user, "/user/<user_id:int>/", methods=["GET"])
    app.add_route(update_user, "/user/<user_id:int>/", methods=["PATCH"])


def create_app():
    app = Sanic("bench_app")
    app.register_listener(on_startup, "before_server_start")
    app.register_listener(on_cleanup, "after_server_stop")

    register_routers(app)
    logger.info("Service started")
    return app
