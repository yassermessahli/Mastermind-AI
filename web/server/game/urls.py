from django.urls import path

from game import views

urlpatterns = [
    path("start/", views.start),
    path("guess/", views.guess),
    path("feedback/", views.feedback),
    path("state/", views.game_state),
    path("reset/", views.reset),
]
