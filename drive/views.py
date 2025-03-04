import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.conf import settings
from .models import GoogleOAuthToken
from django.utils.timezone import now
from django.conf import settings
import datetime
from googleapiclient.discovery import build
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.core.files.storage import default_storage
from django.http import StreamingHttpResponse, HttpResponse
import logging
import io
from googleapiclient.http import MediaIoBaseUpload




def google_login(request):
    auth_url = (
        f"{settings.GOOGLE_AUTH_URL}"
        f"?client_id={settings.DRIVE_CLIENT_ID}"
        f"&redirect_uri={settings.DRIVE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid email profile https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/gmail.readonly"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return redirect(auth_url)

def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code not found"}, status=400)

    token_data = {
        "client_id": settings.DRIVE_CLIENT_ID,
        "client_secret": settings.DRIVE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.DRIVE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(settings.GOOGLE_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    access_token = token_json.get("access_token")
    refresh_token = token_json.get("refresh_token")  
    expires_in = token_json.get("expires_in", 3600)  
    try:
        expires_in = int(expires_in)  
    except (TypeError, ValueError):
        expires_in = 3600  

    if not access_token:
        return JsonResponse({"error": "Access token not received"}, status=400)
    
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_response.json()

    email = user_info.get("email")
    name = user_info.get("name")

    if not email:
        return JsonResponse({"error": "Failed to get user email from Google"}, status=400)

    user, created = User.objects.get_or_create(
        username=email, 
        defaults={"email": email, "first_name": name}
    )
    login(request, user)

    expires_at = now() + datetime.timedelta(seconds=expires_in)
    token_type = token_json.get("token_type", "Bearer")

    token_obj, created = GoogleOAuthToken.objects.get_or_create(
        user=user,
        defaults={
            'access_token': access_token,
            'token_type': token_type,
            'expires_at': expires_at,
            'refresh_token': refresh_token
        }
    )

    if not created:
        token_obj.access_token = access_token
        token_obj.token_type = token_type
        token_obj.expires_at = expires_at
        if refresh_token:
            token_obj.refresh_token = refresh_token
        token_obj.save()

    return redirect('/drive/')


@login_required
def logout_view(request):
    logout(request) 
    return redirect('/drive/') 

def home(request):
    return render(request, 'index.html')

@login_required
def upload_file(request):
    """Upload a file to Google Drive using stored OAuth tokens."""

    try:
        token_obj = GoogleOAuthToken.objects.get(user=request.user)
    except GoogleOAuthToken.DoesNotExist:
        return redirect("drive_login")  

    if token_obj.is_expired():
        return redirect("drive_login")

    credentials = Credentials(
        token=token_obj.access_token,
        refresh_token=token_obj.refresh_token,
        token_uri=settings.GOOGLE_TOKEN_URL, 
        client_id=settings.DRIVE_CLIENT_ID,
        client_secret=settings.DRIVE_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )

    service = build("drive", "v3", credentials=credentials)

    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        file_stream = io.BytesIO(uploaded_file.read())
        media = MediaIoBaseUpload(file_stream, mimetype=uploaded_file.content_type, resumable=True)

        file_metadata = {"name": uploaded_file.name}
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
        ).execute()

        file_id = uploaded_file.get("id")
        return render(request, "upload.html", {"message": f"File uploaded successfully: {file_id}"})

    return render(request, "upload.html")


@login_required
def google_drive_picker(request):
    """Render the Google Picker page."""
    return render(request, "drive_picker.html", {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    })

logger = logging.getLogger(__name__)



@login_required
def download_drive_file(request, file_id):
    """Download a file from Google Drive and send it to the user."""
    try:
        token = request.user.drive_token
    except GoogleOAuthToken.DoesNotExist:
        return HttpResponse("User has not linked their Google Drive account.", status=403)

    if token.is_expired():
        return HttpResponse("Google Drive token has expired. Please reauthenticate.", status=403)

    try:
        creds = Credentials(token.access_token)
        drive_service = googleapiclient.discovery.build("drive", "v3", credentials=creds)

        file_metadata = drive_service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get("name", "downloaded_file")
        mime_type = file_metadata.get("mimeType", "")

        export_formats = {
            "application/vnd.google-apps.document": "application/pdf", 
            "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            "application/vnd.google-apps.presentation": "application/pdf", 
        }

        if mime_type in export_formats:
            export_mime = export_formats[mime_type]
            request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime)
            file_name += ".pdf" if "pdf" in export_mime else ".xlsx"
        else:
            request = drive_service.files().get_media(fileId=file_id)

        # Stream the file to the user
        response = StreamingHttpResponse(request.execute(), content_type=export_mime if mime_type in export_formats else "application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response

    except Exception as e:
        logger.error(f"Error downloading file from Google Drive: {e}", exc_info=True)
        return HttpResponse(f"Error downloading file: {str(e)}", status=500)


@login_required
def fetch_recent_emails(request):
    """Fetch top 5 recent emails from Gmail"""
    try:
        user = request.user
        user_token = GoogleOAuthToken.objects.get(user=user)

        # Check if token is expired
        if user_token.expires_at < now():
                return JsonResponse({"error": "Failed to refresh access token"}, status=400)
        else:
            access_token = user_token.access_token

        # Fetch recent emails
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"maxResults": 5, "labelIds": "INBOX"}
        response = requests.get(settings.GMAIL_API_URL, headers=headers, params=params)

        messages = response.json().get("messages", [])

            # Fetch details of each email
        email_data = []
        for msg in messages:
            msg_id = msg["id"]
            email_response = requests.get(f"{settings.GMAIL_API_URL}/{msg_id}", headers=headers)
            if email_response.status_code == 200:
                email_info = email_response.json()
                headers_list = email_info.get("payload", {}).get("headers", [])
                
                # Extract sender and subject
                sender = next((h["value"] for h in headers_list if h["name"] == "From"), "Unknown Sender")
                subject = next((h["value"] for h in headers_list if h["name"] == "Subject"), "No Subject")
                snippet = email_info.get("snippet", "")

                email_data.append({"id": msg_id, "from": sender, "subject": subject, "snippet": snippet})

        return render(request, "get_emails.html", {"emails": email_data})


    except GoogleOAuthToken.DoesNotExist:
        return JsonResponse({"error": "Google OAuth token not found for this user"}, status=400)
