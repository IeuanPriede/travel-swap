from django.contrib.auth.models import User
from django.db import models


# Create your models here.
# Profile model linked one-to-one with User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Custom fields for the user's profile
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to='profile_images/', default='default.jpg'
        )
    is_visible = models.BooleanField(default=True)

    # House-specific fields
    house_description = models.TextField(blank=True)
    preferred_destinations = models.CharField(max_length=255, blank=True)
    available_dates = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username
      

# New model to support multiple images per profile
class HouseImage(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='house_images'
    )
    image = models.ImageField(upload_to='house_images/')

    def __str__(self):
        return f"Image for {self.profile.user.username}"