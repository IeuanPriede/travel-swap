from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from notifications.context_processors import unread_notifications


class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='charlie', password='pass123')

    def test_create_notification(self):
        notif = Notification.objects.create(
            user=self.user,
            message="You have a new match!",
            link="https://example.com/match"
        )

        self.assertEqual(notif.user, self.user)
        self.assertEqual(notif.message, "You have a new match!")
        self.assertEqual(notif.link, "https://example.com/match")
        self.assertFalse(notif.is_read)
        self.assertIsNotNone(notif.created_at)
        self.assertLessEqual(
            notif.created_at, timezone.now() + timedelta(seconds=1))

        expected_str = (
            f"Notification for {self.user.username}: {notif.message}"
        )
        self.assertEqual(str(notif), expected_str)
        self.assertEqual(str(notif), expected_str)


class NotificationViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='pass123')
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass123')

        self.notif1 = Notification.objects.create(
            user=self.user, message="Test 1", is_read=False)
        self.notif2 = Notification.objects.create(
            user=self.user,
            message="Test 2",
            is_read=False,
            link="/some-link/"
        )
        self.notif3 = Notification.objects.create(
            user=self.other_user, message="Other user", is_read=False)

    def test_mark_all_read(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('mark_all_read'), HTTP_REFERER='/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/dashboard/')
        self.notif1.refresh_from_db()
        self.notif2.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
        self.assertTrue(self.notif2.is_read)

    def test_dismiss_notification(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('dismiss_notification', args=[self.notif1.id]),
            HTTP_REFERER='/')
        self.assertRedirects(response, '/')
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

    def test_mark_notification_read_with_link(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(
            reverse('mark_notification_read', args=[self.notif2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.notif2.link)

    def test_dismiss_notification_unauthorized_access(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('dismiss_notification', args=[self.notif3.id]))
        self.assertEqual(response.status_code, 404)


class NotificationContextProcessorTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='pass123')

    def test_returns_queryset_for_authenticated_user(self):
        Notification.objects.create(
            user=self.user, message='Test', is_read=False)
        request = self.factory.get('/')
        request.user = self.user

        context = unread_notifications(request)
        self.assertIn('unread_notifications', context)
        self.assertEqual(context['unread_notifications'].count(), 1)

    def test_returns_empty_queryset_if_all_read(self):
        Notification.objects.create(
            user=self.user, message='Test', is_read=True)
        request = self.factory.get('/')
        request.user = self.user

        context = unread_notifications(request)
        self.assertIn('unread_notifications', context)
        self.assertEqual(context['unread_notifications'].count(), 0)

    def test_returns_empty_list_for_anonymous_user(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        context = unread_notifications(request)
        self.assertIn('unread_notifications', context)
        self.assertEqual(context['unread_notifications'], [])
