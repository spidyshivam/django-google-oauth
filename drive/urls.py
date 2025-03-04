from django.urls import path
from .views import google_login, google_callback, logout_view, upload_file, home, google_drive_picker, download_drive_file, fetch_recent_emails

urlpatterns = [
    path('', home, name="drive_home"),
    path("auth/login/", google_login, name="drive_login"),
    path("auth/callback/", google_callback, name="drive_callback"),
    path("logout/", logout_view, name="drive_logout"),
    path("upload/", upload_file, name="upload_file"),
    path("picker/", google_drive_picker, name="google_drive_picker"),
    path("download/<str:file_id>/", download_drive_file, name="download_drive_file"),
    path("get_emails/", fetch_recent_emails, name="get_emails"),
]

