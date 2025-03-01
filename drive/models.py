
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import datetime

class GoogleOAuthToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="drive_token")
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_type = models.CharField(max_length=50)
    expires_at = models.DateTimeField()

    def is_expired(self):
        """Check if the access token is expired."""
        return now() >= self.expires_at

    def update_token(self, token_data):
        """Update token values when refreshed."""
        self.access_token = token_data.get("access_token", self.access_token)
        self.token_type = token_data.get("token_type", self.token_type)
        
        expires_in = token_data.get("expires_in", 3600)  
        self.expires_at = now() + datetime.timedelta(seconds=expires_in)

        if "refresh_token" in token_data:
            self.refresh_token = token_data["refresh_token"]

        self.save()

    def __str__(self):
        return f"{self.user.username} - Google Token"
