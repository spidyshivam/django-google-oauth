# django-google-oauth

# Django Google Integration Project

This project integrates Google authentication and Google Drive functionality into a Django web application. It includes authentication via Google OAuth, Google Drive file handling, and a chat module with WebSocket support.

## Features
- Google Authentication (Login, Callback, Logout)
- Google Drive File Upload, Download, and Picker Integration
- Chat System with WebSocket Support
- Django Admin Panel for Management

## Requirements
Ensure you have Python installed and set up a virtual environment.

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Apply Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

## Environment Variables
Set up the following environment variables in your `.env` file or `settings.py`:

```sh
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

DRIVE_CLIENT_ID="your-drive-client-id"
DRIVE_CLIENT_SECRET="your-drive-client-secret"
GOOGLE_API_KEY="your-google-api-key"
```

## Routes

### Global Routes (`djangogoogle/urls.py`)
- `/admin/` → Django Admin Panel
- `/auth/login/` → Google Login
- `/auth/callback/` → Google OAuth Callback
- `/drive/` → Google Drive Module
- `/chat/` → Chat Module

### Google Drive Routes (`drive/urls.py`)
- `/drive/` → Drive Home
- `/drive/auth/login/` → Google Login for Drive
- `/drive/auth/callback/` → OAuth Callback for Drive
- `/drive/logout/` → Logout
- `/drive/upload/` → Upload File
- `/drive/picker/` → Google Drive Picker
- `/drive/download/<file_id>/` → Download File

### Chat Routes (`chat/urls.py`)
- `/chat/` → Chat List
- `/chat/<username>/` → Chat Detail
- `ws/chat/<username>/` → WebSocket Connection for Chat

## Running the Project
```sh
python manage.py runserver
```
/drive/ is the home , from there you can access everything 

deployed at - https://django-google-oauth-production.up.railway.app/drive/

## Contributing
Feel free to fork and contribute to this project by submitting a pull request.

## License
This project is licensed under the MIT License.

