from django.http import HttpResponse
from django.urls import path

from . import views


def passer(request):
    return HttpResponse(status=503)


urlpatterns = [
    path('register', views.register),
    path('auth', views.auth)
]
