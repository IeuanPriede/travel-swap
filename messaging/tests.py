from django.test import TestCase
from django.contrib.auth.models import User
from messaging.models import Message, BookingRequest
from datetime import timedelta
from django.utils import timezone


class MessageModelTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            username='alice', password='testpass123')
        self.recipient = User.objects.create_user(
            username='bob', password='testpass123')

    def test_create_message(self):
        content = "Hello, Bob!"
        msg = Message.objects.create(
            sender=self.sender, recipient=self.recipient, content=content)

        self.assertEqual(msg.sender, self.sender)
        self.assertEqual(msg.recipient, self.recipient)
        self.assertEqual(msg.content, content)
        self.assertIsNotNone(msg.timestamp)
        self.assertLessEqual(
            msg.timestamp, timezone.now() + timedelta(seconds=1))
        self.assertEqual(
            str(msg),
            f"From {self.sender} to {self.recipient} at {msg.timestamp}"
        )


class BookingRequestModelTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            username='alice', password='pass123')
        self.recipient = User.objects.create_user(
            username='bob', password='pass123')

    def test_create_booking_request(self):
        booking = BookingRequest.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            requested_dates="2025-08-01 to 2025-08-10",
            message="We'd love to stay!",
            last_action_by=self.sender
        )

        self.assertEqual(booking.sender, self.sender)
        self.assertEqual(booking.recipient, self.recipient)
        self.assertEqual(booking.requested_dates, "2025-08-01 to 2025-08-10")
        self.assertEqual(booking.message, "We'd love to stay!")
        self.assertEqual(booking.status, "pending")
        self.assertIsNotNone(booking.created_at)
        self.assertIsNone(booking.responded_at)
        self.assertEqual(booking.last_action_by, self.sender)
        self.assertLessEqual(
            booking.created_at, timezone.now() + timedelta(seconds=1))

        expected_str = (
            f"{self.sender.username} → {self.recipient.username}: "
            f"{booking.requested_dates} ({booking.status})"
        )
        self.assertEqual(str(booking), expected_str)