from django.http import HttpResponse
from django.urls import path

from . import views


def passer(request):
    return HttpResponse(status=503)


urlpatterns = [
    # registration and authorization API
    path('register', views.register),
    path('auth', views.auth),

    # API paths for managing access tokens
    path('control/tokens', passer),
    path('control/ttokens', passer)
]
