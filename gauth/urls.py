from django.urls import path
from .views import google_login, google_callback

urlpatterns = [
    path("auth/login/", google_login, name="google-login"),
    path("auth/callback/", google_callback, name="google-callback"),
]
