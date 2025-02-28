import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from django.utils.timezone import now
import datetime



# Step 1: Redirect user to Google login
def google_login(request):
    auth_url = (
        f"{settings.GOOGLE_AUTH_URL}"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return redirect(auth_url)

# Step 2: Google OAuth Callback
def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code not found"}, status=400)

    # Exchange authorization code for access token
    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(settings.GOOGLE_TOKEN_URL, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get("access_token")

    # Fetch user info
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(settings.GOOGLE_USER_INFO_URL, headers=headers)
    user_data = user_response.json()

    return JsonResponse({"token": token_json, "user": user_data})
