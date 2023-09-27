from django.urls import path

from . import views


urlpatterns = [
    path('register', views.register),
    path('auth', views.auth),
    path('control/tokens', views.control_tokens),
    path('control/tokens', views.control_tokens),
    path('control/ttokens', views.control_ttokens)
]
