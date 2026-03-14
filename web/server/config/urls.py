from django.urls import include, path

urlpatterns = [
    path("api/game/", include("game.urls")),
]
