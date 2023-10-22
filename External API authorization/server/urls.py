from django.http import HttpResponse
from django.urls import path

from . import views


def passer(_):
    return HttpResponse(status=503)


def ratelimited(*_):
    return HttpResponse(status=429)


urlpatterns = [
    path('register', views.register),
    path('auth', views.auth)
]
