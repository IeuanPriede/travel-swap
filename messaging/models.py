from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"


class BookingRequest(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='booking_requests_sent')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='booking_requests_received')
    requested_dates = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('amended', 'Amended'),
        ('denied', 'Denied'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    last_action_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking_last_actor'
    )

    def __str__(self):
        return (
            f"{self.sender.username} → {self.recipient.username}: "
            f"{self.requested_dates} ({self.status})"
        )
