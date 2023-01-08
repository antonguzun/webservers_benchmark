from django.urls import path
from .views import ping, plain, to_json, UserView

urlpatterns = [
    path("ping/", ping),
    path("plain/", plain),
    path("to_json/", to_json),
    path("user/<int:user_id>/", UserView.as_view()),
]
