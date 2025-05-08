from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Profile(models.Model):
    # One-to-one link with Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Custom fields for the user's profile
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='profile_images/', default='default.jpg')
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username