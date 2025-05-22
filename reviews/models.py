from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_written")
    reviewee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'reviewee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer} → {self.reviewee} ({self.rating} stars)"
