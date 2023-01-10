import json
import logging

from asgiref.sync import sync_to_async
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View

from .models import User

logger = logging.getLogger("django_async")


class DisableCSRFMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)
        response = self.get_response(request)
        return response


def get_user(user_id):
    return User.objects.get(user_id=user_id)


def update_user(user_id, data):
    user = User.objects.get(user_id=user_id)
    user.username = data["username"]
    user.email = data["email"]
    user.save()
    return user


class UserView(View):
    def get(self, request: HttpRequest, user_id: int):
        if request.headers.get("token") != "hardcoded_token":
            return JsonResponse(data={"description": "unauthorized"}, status=403)
        logger.info(f"getting user with id {user_id}")
        try:
            user = get_user(user_id=user_id)
            return JsonResponse(
                data=dict(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    is_archived=user.is_archived,
                )
            )
        except User.DoesNotExist:
            return JsonResponse(data='{"description": "user not found"}', status=404)

    def patch(self, request: HttpRequest, user_id: int):
        if request.headers.get("token") != "hardcoded_token":
            return JsonResponse(data={"description": "unauthorized"}, status=403)
        logger.info(f"try to update with id {user_id}")
        data = dict(json.loads(request.body.decode()))
        user = update_user(
            user_id=user_id, data=data
        )
        if user:
            return JsonResponse(
                data=dict(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    is_archived=user.is_archived,
                )
            )
        return JsonResponse(data='{"description": "user not found"}', status=404)


def to_json(request: HttpRequest):
    if request.headers.get("token") != "hardcoded_token":
        return JsonResponse(data={"description": "unauthorized"}, status=403)
    param1 = request.GET.get("param1")
    param2 = request.GET.get("param2")
    param3 = request.GET.get("param3")
    return JsonResponse(data={"param1": param1, "param2": param2, "param3": param3})


def plain(request: HttpRequest):
    if request.headers.get("token") != "hardcoded_token":
        return JsonResponse(data={"description": "unauthorized"}, status=403)
    param1 = request.GET.get("param1")
    param2 = request.GET.get("param2")
    param3 = request.GET.get("param3")
    return HttpResponse(content=f"{param1=}, {param2=}, {param3=}")


def ping(_: HttpRequest):
    return HttpResponse(content="pong")
