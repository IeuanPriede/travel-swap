from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import mimetypes
from django_countries.fields import CountryField


# Create your models here.
# Profile model linked one-to-one with User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Custom fields for the user's profile
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    location = CountryField(blank_label='(select country)', blank=True)
    image = models.ImageField(
        upload_to='profile_images/', default='default.jpg'
        )
    is_visible = models.BooleanField(default=True)

    # House-specific fields
    house_description = models.TextField(blank=True)
    preferred_destinations = models.CharField(max_length=255, blank=True)
    available_dates = models.CharField(max_length=255, blank=True)

    # House criteria fields
    pets_allowed = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    more_than_3_bedrooms = models.BooleanField(default=False)
    near_beach = models.BooleanField(default=False)
    in_mountains = models.BooleanField(default=False)
    in_city = models.BooleanField(default=False)
    in_rural = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.location}'


@deconstructible
class ImageValidator:
    def __init__(self, max_size_mb=2, allowed_types=None):
        self.max_size_mb = max_size_mb
        self.allowed_types = allowed_types or [
            'image/jpeg',
            'image/png',
            'image/pjpeg',
            'image/jpg',
            ]

    def __call__(self, file):
        # Size check
        limit = self.max_size_mb * 1024 * 1024
        if file.size > limit:
            raise ValidationError(
                f'Maximum file size is {self.max_size_mb}MB.')

        # Safely guess content type from file name
        guessed_type, _ = mimetypes.guess_type(file.name)
        print(
            "DEBUG - Guessed MIME type:",
            guessed_type, "for file:", file.name)

        # Robust type check
        if guessed_type is None or guessed_type not in self.allowed_types:
            raise ValidationError('Only JPEG and PNG images are allowed.')


# New model to support multiple images per profile
class HouseImage(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='house_images'
    )
    image = models.ImageField(upload_to='house_images/',
                              validators=[ImageValidator(max_size_mb=2)])

    def __str__(self):
        return f"Image for {self.profile.user.username}"


class MatchResponse(models.Model):
    # The user giving a thumbs up or down.
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='responses_sent')
    # The profile being reviewed.
    to_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='responses_received')
    # True for thumbs up, false for thumbs down.
    liked = models.BooleanField()
    # The timestamp of the response.
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure that a user can only respond once to a profile.
        unique_together = ('from_user', 'to_profile')

    def __str__(self):
        # Return a string representation of the response.
        status = "liked" if self.liked else "disliked"
        return (
            f"{self.from_user.username} {status} "
            f"{self.to_profile.user.username}"
        )
