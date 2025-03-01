from django.urls import path
from .views import chat_list, chat_detail

urlpatterns = [
    path("", chat_list, name="chat_list"),
    path("<str:username>/", chat_detail, name="chat_detail"),
]