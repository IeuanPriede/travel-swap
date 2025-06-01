from django.test import TestCase
from django.contrib.auth.models import User
from messaging.models import Message
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
