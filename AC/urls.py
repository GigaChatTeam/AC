from django.urls import path

from . import views


urlpatterns = [
    # registration and authorization API
    path('register', views.register),
    path('auth', views.auth),

    # API paths for managing Access tokens
    path('confirm/email', views.Confirmation.email),

    # API paths for managing access tokens
    path('control/tokens', views.control_tokens),
    path('control/ttokens', views.control_ttokens)
]
