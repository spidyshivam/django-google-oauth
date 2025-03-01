
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_list(request):
    """Shows all chats where the user is involved."""
    users = User.objects.exclude(id=request.user.id)
    return render(request, "chat_list.html", {"users": users})

@login_required
def chat_detail(request, username):
    """Shows chat messages between the logged-in user and another user."""
    other_user = get_object_or_404(User, username=username)
    messages = ChatMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("timestamp")

    return render(request, "chat_detail.html", {"messages": messages, "other_user": other_user})