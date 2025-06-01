from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from profiles.models import Profile, HouseImage, MatchResponse
from django.core.exceptions import ValidationError
import io
import json
from PIL import Image
from profiles.forms import (
    CustomUserCreationForm,
    UserForm,
    ProfileForm,
    ImageForm,
    ContactForm
)
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from messaging.models import BookingRequest
from notifications.models import Notification
from django.utils.timezone import now
from profiles.views import (
    get_latest_booking,
    check_if_matched,
    user_is_matched
)
User = get_user_model()


class ProfileModelTest(TestCase):
    def test_profile_str(self):
        user = User.objects.create(username='alice')
        profile = Profile.objects.create(user=user, location='GB')
        self.assertEqual(str(profile), 'alice - GB')

    def test_profile_defaults(self):
        user = User.objects.create(username='bob')
        profile = Profile.objects.create(user=user)
        self.assertTrue(profile.is_visible)
        self.assertFalse(profile.pets_allowed)
        self.assertEqual(profile.first_name, '')


class HouseImageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='charlie')
        self.profile = Profile.objects.create(user=self.user)

    def test_house_image_str(self):
        image = HouseImage.objects.create(
            profile=self.profile,
            image=SimpleUploadedFile(
                "test.jpg", b"file_content", content_type="image/jpeg")
        )
        self.assertEqual(str(image), "Image for charlie")

    def test_image_validator_rejects_large_file(self):
        big_file = SimpleUploadedFile(
            "big.jpg", b"x" * (3 * 1024 * 1024), content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            HouseImage(profile=self.profile, image=big_file).full_clean()

    def test_image_validator_rejects_invalid_type(self):
        bad_file = SimpleUploadedFile(
            "script.js", b"alert(1)", content_type="application/javascript")
        with self.assertRaises(ValidationError):
            HouseImage(profile=self.profile, image=bad_file).full_clean()


class MatchResponseModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='dave')
        self.user2 = User.objects.create(username='emma')
        self.profile2 = Profile.objects.create(user=self.user2)

    def test_match_response_str(self):
        match = MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)
        self.assertEqual(str(match), "dave liked emma")

    def test_match_response_unique_constraint(self):
        MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)
        with self.assertRaises(Exception):
            MatchResponse.objects.create(
                from_user=self.user1, to_profile=self.profile2, liked=False)


class TestProfileForms(TestCase):

    def test_custom_user_creation_valid_data(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'user@example.com',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123'
        })
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_blank_username(self):
        form = CustomUserCreationForm(data={
            'username': '   ',
            'email': 'user@example.com',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_custom_user_creation_blank_email(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': '   ',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_form_blank_username(self):
        user = User.objects.create(username='user', email='user@example.com')
        form = UserForm(instance=user, data={
            'username': '   ',
            'email': 'user@example.com'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_form_blank_email(self):
        user = User.objects.create(username='user', email='user@example.com')
        form = UserForm(instance=user, data={
            'username': 'user',
            'email': '   '
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_profile_form_blank_bio(self):
        form = ProfileForm(data={
            'bio': '   ',
            'house_description': 'Lovely home',
            'location': 'US'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)

    def test_profile_form_blank_house_description(self):
        form = ProfileForm(data={
            'bio': 'We are a nice couple.',
            'house_description': '   ',
            'location': 'US'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('house_description', form.errors)

    def test_image_form_large_file(self):
        big_file = io.BytesIO(b"x" * (2 * 1024 * 1024 + 1))
        big_file.name = 'test.jpg'
        form = ImageForm(files={
            'image': SimpleUploadedFile('test.jpg', big_file.getvalue())
        })
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_image_form_invalid_format(self):
        bad_file = io.BytesIO(b"notanimage")
        bad_file.name = 'test.txt'
        form = ImageForm(files={
            'image': SimpleUploadedFile('test.txt', bad_file.getvalue())
        })
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_contact_form_blank_name(self):
        form = ContactForm(data={
            'name': '   ',
            'email': 'user@example.com',
            'subject': 'Test Subject',
            'message': 'Hello!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_contact_form_blank_email(self):
        form = ContactForm(data={
            'name': 'John',
            'email': '   ',
            'subject': 'Test Subject',
            'message': 'Hello!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_contact_form_blank_subject(self):
        form = ContactForm(data={
            'name': 'John',
            'email': 'user@example.com',
            'subject': '   ',
            'message': 'Hello!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

    def test_contact_form_blank_message(self):
        form = ContactForm(data={
            'name': 'John',
            'email': 'user@example.com',
            'subject': 'Hello',
            'message': '   '
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            location='FR',
            bio='Test bio',
            house_description='Nice house.',
            available_dates='2025-07-01 to 2025-07-15',
        )

    def test_profile_view_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('profiles'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertIn('profile', response.context)
        self.assertIn('house_images', response.context)
        self.assertIn('reviews', response.context)
        self.assertIn('average_rating', response.context)
        self.assertEqual(response.context['profile'], self.profile)

    def test_profile_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('profiles'))
        self.assertRedirects(
            response, '/accounts/login/?next=/profiles/profile'
        )


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass', email='test@example.com'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            location='FR',
            bio='Test bio',
            house_description='Nice house.',
            available_dates='2025-07-01 to 2025-07-15',
        )
        self.edit_url = reverse('edit_profile')

    def test_edit_profile_redirects_if_not_logged_in(self):
        response = self.client.get(self.edit_url)
        self.assertRedirects(
            response, f'/accounts/login/?next={self.edit_url}')

    def test_edit_profile_view_get_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/edit_profile.html')
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)
        self.assertIn('formset', response.context)

    def test_edit_profile_post_valid_data(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.edit_url, {
            'username': 'newname',
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Updated bio',
            'location': 'FR',
            'house_description': 'Updated house.',
            'available_dates': '2025-08-01 to 2025-08-15',
        })
        self.assertRedirects(response, reverse('profiles'))
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.username, 'newname')
        self.assertEqual(self.profile.bio, 'Updated bio')

    def test_edit_profile_post_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.edit_url, {
            'username': '',  # Invalid
            'email': '',
            'bio': '',
            'house_description': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'user_form', 'username', 'This field is required.')
        self.assertFormError(
            response, 'user_form', 'username', 'This field is required.')
        self.assertFormError(
            response, 'user_form', 'username', 'This field is required.')
        self.assertFormError(
            response, 'user_form', 'username', 'This field is required.')


def generate_test_image():
    img_io = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="red")
    image.save(img_io, format="JPEG")
    img_io.seek(0)
    return SimpleUploadedFile(
        "test.jpg", img_io.read(), content_type="image/jpeg")


class UploadImagesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='imguser', password='imgpass')
        Profile.objects.create(
            user=self.user, location='FR', bio='Bio',
            house_description='Desc',
            available_dates='2025-07-01 to 2025-07-15'
        )
        self.url = reverse('upload_images')

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_upload_valid_image(self):
        self.client.login(username='imguser', password='imgpass')

        valid_image = generate_test_image()

        post_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-0-image': valid_image,
        }

        response = self.client.post(self.url, post_data, follow=True)

        self.assertRedirects(response, reverse('edit_profile'))

        self.assertEqual(
            HouseImage.objects.filter(profile=self.user.profile).count(), 1)

    def test_upload_invalid_image(self):
        self.client.login(username='imguser', password='imgpass')
        invalid_file = SimpleUploadedFile(
            "test.txt", b"not an image", content_type="text/plain")

        response = self.client.post(self.url, {
            'form-0-image': invalid_file,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
        }, follow=True)

        self.assertContains(response, "There was a problem updating images.")


class DeleteProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='deleteuser', password='deletepass'
        )
        # ✅ Create an associated Profile so edit_profile doesn't 404
        Profile.objects.create(
            user=self.user,
            location='FR',
            bio='Test bio',
            house_description='Nice house',
            available_dates='2025-07-01 to 2025-07-15'
        )
        self.url = reverse('delete_profile')

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_delete_with_correct_password(self):
        self.client.login(username='deleteuser', password='deletepass')
        response = self.client.post(self.url, {'password': 'deletepass'})
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(User.objects.filter(username='deleteuser').exists())

    def test_delete_with_incorrect_password(self):
        self.client.login(username='deleteuser', password='deletepass')
        response = self.client.post(self.url, {'password': 'wrongpass'})
        self.assertRedirects(response, reverse('edit_profile'))
        self.assertTrue(User.objects.filter(username='deleteuser').exists())


class RegisterViewTest(TestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_register_view_get(self):
        """Ensure the registration page loads correctly with a blank form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('form', response.context)

    def test_register_view_post_valid_data(self):
        """Ensure a new user is created and logged in with valid data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!',
        }
        response = self.client.post(self.url, form_data)
        self.assertRedirects(response, reverse('profiles'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid_data(self):
        """Ensure invalid form submission re-renders the form with errors."""
        form_data = {
            'username': '',
            'email': 'bademail',
            'password1': '123',
            'password2': '456',
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertFormError(
            response, 'form', 'username', 'This field is required.')
        self.assertFormError(
            response, 'form', 'password2',
            'The two password fields didn’t match.'
        )


User = get_user_model()


def generate_test_image_file():
    """Helper to generate a valid in-memory JPEG file."""
    img_io = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="blue")
    image.save(img_io, format="JPEG")
    img_io.seek(0)
    return SimpleUploadedFile(
        "test.jpg", img_io.read(), content_type="image/jpeg")


class DeleteImageViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', password='pass123')
        self.other_user = User.objects.create_user(
            username='intruder', password='pass456')

        self.profile = Profile.objects.create(
            user=self.owner,
            location='US',
            bio='Test bio',
            house_description='Test house',
            available_dates='2025-08-01 to 2025-08-15'
        )

        self.image = HouseImage.objects.create(
            profile=self.profile,
            image=generate_test_image_file()
        )

        self.url = reverse('delete_image', args=[self.image.id])

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_forbidden_if_not_owner(self):
        self.client.login(username='intruder', password='pass456')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_successful_deletion_by_owner(self):
        self.client.login(username='owner', password='pass123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(HouseImage.objects.filter(id=self.image.id).exists())

    def test_invalid_method_returns_400(self):
        self.client.login(username='owner', password='pass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Invalid request"}
        )


class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', password='pass123')
        self.other_user = User.objects.create_user(
            username='bob', password='pass456')

        self.profile = Profile.objects.create(
            user=self.other_user,
            location='FR',
            bio='Test bio',
            house_description='Nice place',
            available_dates='2025-07-01 to 2025-07-15',
            is_visible=True,
        )

    def test_home_view_unauthenticated(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('profile', response.context)

    def test_home_view_authenticated_excludes_own_and_responded(self):
        self.client.login(username='alice', password='pass123')

        # Simulate response to other_user's profile
        MatchResponse.objects.create(
            from_user=self.user,
            to_profile=self.profile,
            liked=True
        )

        response = self.client.get(reverse('home'))
        # No profiles should be shown
        self.assertIsNone(response.context['profile'])

    def test_home_view_with_filters(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.profile)

    def test_home_view_with_location_filter(self):
        response = self.client.get(reverse('home') + '?location=FR')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.profile)

    def test_home_view_with_valid_date_range(self):
        response = self.client.get(
            reverse('home') + '?dates=2025-07-01 to 2025-07-15')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.profile)

    def test_home_view_with_invalid_date_range(self):
        response = self.client.get(reverse('home') + '?dates=badformat')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)

    def test_home_view_ajax_returns_partial(self):
        response = self.client.get(reverse('home'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn('next_profile_html', response.json())


class NextProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='viewer', password='testpass')
        self.other_user = User.objects.create_user(
            username='other', password='otherpass')

        self.other_profile = Profile.objects.create(
            user=self.other_user,
            location='FR',
            bio='Test bio',
            house_description='Nice house',
            available_dates='2025-07-01 to 2025-07-15',
            is_visible=True
        )

        self.url = reverse('next_profile')

    def test_post_without_session_returns_fallback_html(self):
        # Hide the profile so the fallback logic triggers
        self.other_profile.is_visible = False
        self.other_profile.save()

        response = self.client.post(
            self.url, content_type='application/json',
            data=json.dumps({'filters': {}})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No more profiles available", response.json()['next_profile_html'])

    def test_post_with_valid_session_returns_profile_html(self):
        self.client.login(username='viewer', password='testpass')
        session = self.client.session
        session['profile_sequence'] = [self.other_profile.id]
        session['current_index'] = 0
        session.save()

        response = self.client.post(
            self.url, content_type='application/json',
            data=json.dumps({'filters': {}})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Next Home", response.json()['next_profile_html'])

    def test_post_with_only_one_profile_shows_alert(self):
        self.client.login(username='viewer', password='testpass')
        session = self.client.session
        session['profile_sequence'] = [self.other_profile.id]
        session['current_index'] = 1  # Already seen the only profile
        session.save()

        response = self.client.post(
            self.url, content_type='application/json',
            data=json.dumps({'filters': {}})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "only matching profile", response.json()['next_profile_html'])

    def test_get_method_disallowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class LikeProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='viewer', password='testpass', email='viewer@example.com')
        self.user2 = User.objects.create_user(
            username='other', password='otherpass', email='other@example.com')

        self.profile2 = Profile.objects.create(
            user=self.user2,
            location='FR',
            bio='Test bio',
            house_description='Nice house',
            available_dates='2025-07-01 to 2025-07-15',
            is_visible=True
        )

        self.url = reverse('like_profile')

    def test_like_profile_creates_matchresponse(self):
        self.client.login(username='viewer', password='testpass')
        response = self.client.post(
            self.url,
            data=json.dumps({'profile_id': self.profile2.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('You liked', data['message'])

        match = MatchResponse.objects.get(
            from_user=self.user1, to_profile=self.profile2)
        self.assertTrue(match.liked)


class UnlikeProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass')
        self.profile = Profile.objects.create(
            user=self.other_user,
            location='US',
            bio='Bio',
            house_description='House',
            is_visible=True
        )
        self.match = MatchResponse.objects.create(
            from_user=self.user,
            to_profile=self.profile,
            liked=True
        )
        self.url = reverse('unlike_profile', args=[self.profile.id])

    def test_unlike_profile_removes_match_and_redirects(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url)

        # Confirm redirect to travel log
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('travel_log'))

        # Confirm MatchResponse deleted
        self.assertFalse(
            MatchResponse.objects.filter(
                from_user=self.user,
                to_profile=self.profile,
                liked=True
            ).exists()
        )

        # Confirm success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("unliked" in str(m) for m in messages))


class TravelLogMutualMatchTest(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(
            username='viewer', password='pass')
        self.other = User.objects.create_user(
            username='other', password='pass')

        self.other_profile = Profile.objects.create(
            user=self.other,
            location='US',
            bio='Other bio',
            house_description='Other house',
            available_dates='2025-07-01 to 2025-07-15',
            is_visible=True
        )

        # Viewer likes other
        MatchResponse.objects.create(
            from_user=self.viewer,
            to_profile=self.other_profile,
            liked=True
        )

        # Other also likes viewer (mutual match)
        viewer_profile = Profile.objects.create(
            user=self.viewer,
            location='FR',
            bio='Viewer bio',
            house_description='Viewer house',
            available_dates='2025-08-01 to 2025-08-15',
            is_visible=True
        )

        MatchResponse.objects.create(
            from_user=self.other,
            to_profile=viewer_profile,
            liked=True
        )

    def test_travel_log_mutual_match_flag(self):
        self.client.login(username='viewer', password='pass')
        response = self.client.get(reverse('travel_log'))
        self.assertEqual(response.status_code, 200)

        liked_profiles = response.context['liked_profiles']
        self.assertEqual(len(liked_profiles), 1)
        self.assertTrue(getattr(liked_profiles[0], 'is_mutual', False))


class ViewProfileViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='pass123', email='user1@example.com')
        self.user2 = User.objects.create_user(
            username='user2', password='pass456', email='user2@example.com')

        self.profile1 = Profile.objects.create(
            user=self.user1,
            location='US',
            bio='Bio 1',
            house_description='House 1',
            available_dates='2025-08-01 to 2025-08-15'
        )

        self.profile2 = Profile.objects.create(
            user=self.user2,
            location='FR',
            bio='Bio 2',
            house_description='House 2',
            available_dates='2025-08-10 to 2025-08-20'
        )

        # Ensure they are a match
        MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)
        MatchResponse.objects.create(
            from_user=self.user2, to_profile=self.profile1, liked=True)

        self.url = reverse('view_profile', args=[self.user2.id])

    def test_view_profile_get_authenticated(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/view_profile.html')
        self.assertEqual(response.context['profile_user'], self.user2)
        self.assertTrue(response.context['is_match'])
        self.assertIn('message_form', response.context)
        self.assertIn('booking_form', response.context)
        self.assertIn('review_form', response.context)


class BookingUtilsTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender', password='pass')
        self.recipient = User.objects.create_user(
            username='recipient', password='pass')
        self.profile = Profile.objects.create(
            user=self.recipient,
            location='US',
            bio='Test bio',
            house_description='Nice house',
            available_dates='2025-08-01 to 2025-08-15'
        )

    def test_get_latest_booking_returns_most_recent(self):
        BookingRequest.objects.create(
            sender=self.sender, recipient=self.recipient,
            requested_dates='2025-08-01 to 2025-08-10',
            created_at=now()
        )
        later = BookingRequest.objects.create(
            sender=self.recipient, recipient=self.sender,
            requested_dates='2025-08-15 to 2025-08-20',
            created_at=now()
        )

        latest = get_latest_booking(self.sender, self.recipient)
        self.assertEqual(latest, later)


class HandleBookingRequestTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(
            username='user1', password='pass1', email='u1@example.com')
        self.profile1 = Profile.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(
            username='user2', password='pass2', email='u2@example.com')
        self.profile2 = Profile.objects.create(user=self.user2)

        self.booking = BookingRequest.objects.create(
            sender=self.user1,
            recipient=self.user2,
            requested_dates='2025-07-01 to 2025-07-15',
            status='pending',
        )

        self.url = reverse('view_profile', args=[self.user2.id])
        self.client.login(username='user1', password='pass1')

    def test_handle_booking_request_valid(self):
        response = self.client.post(self.url, {
            'request_booking': '1',
            'requested_dates': '2025-08-10 to 2025-08-15',
        }, follow=True)

        # Booking was created
        self.assertTrue(
            BookingRequest.objects.filter(
                sender=self.user1, recipient=self.user2).exists()
        )

        # Redirected to view_profile
        self.assertRedirects(response, self.url)

        # Notification created
        self.assertTrue(
            Notification.objects.filter(user=self.user2).exists()
        )


class HandleBookingResponseTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='alice', password='pass')
        self.recipient = User.objects.create_user(
            username='bob', password='pass')

        Profile.objects.create(user=self.sender)
        Profile.objects.create(user=self.recipient)

        self.booking = BookingRequest.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            requested_dates='2025-08-01 to 2025-08-10'
        )
        self.url = reverse('view_profile', args=[self.sender.id])

    def test_handle_booking_response_accept(self):
        self.client.login(username='bob', password='pass')
        response = self.client.post(self.url, {
            'respond_booking': 'accepted'
        })

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'accepted')
        self.assertRedirects(response, self.url)

    def test_handle_booking_response_amend(self):
        self.client.login(username='bob', password='pass')
        response = self.client.post(self.url, {
            'respond_booking': 'amended',
            'amended_dates': '2025-08-15 to 2025-08-20'
        })

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'amended')
        self.assertEqual(
            self.booking.requested_dates, '2025-08-15 to 2025-08-20')
        self.assertRedirects(response, self.url)


class HandleBookingCancelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1', password='pass1', email='user1@example.com')
        self.user2 = User.objects.create_user(
            username='user2', password='pass2', email='user2@example.com')
        Profile.objects.create(user=self.user1)
        Profile.objects.create(user=self.user2)

        self.booking = BookingRequest.objects.create(
            sender=self.user1,
            recipient=self.user2,
            requested_dates='2025-07-20 to 2025-07-25',
            status='accepted'
        )
        self.url = reverse('view_profile', args=[self.user2.id])
        self.client.login(username='user1', password='pass1')

    def test_handle_booking_cancel(self):
        response = self.client.post(self.url, {
            'cancel_booking': '1',
        }, follow=True)

        # Booking is deleted
        self.assertFalse(
            BookingRequest.objects.filter(id=self.booking.id).exists()
        )

        # Notification is created
        self.assertTrue(
            Notification.objects.filter(user=self.user2).exists()
        )

        # Redirect back to view_profile
        self.assertRedirects(response, self.url)


class CheckIfMatchedTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='pass1')
        self.user2 = User.objects.create_user(
            username='user2', password='pass2')
        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

    def test_check_if_matched_true(self):
        MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)
        MatchResponse.objects.create(
            from_user=self.user2, to_profile=self.profile1, liked=True)

        result = check_if_matched(self.user1, self.user2)
        self.assertTrue(result)

    def test_check_if_matched_false_if_one_sided(self):
        MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)

        result = check_if_matched(self.user1, self.user2)
        self.assertFalse(result)

    def test_check_if_matched_false_if_none(self):
        result = check_if_matched(self.user1, self.user2)
        self.assertFalse(result)


class UserIsMatchedTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='pass1')
        self.user2 = User.objects.create_user(
            username='user2', password='pass2')
        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

    def test_user_is_matched_true(self):
        MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)
        MatchResponse.objects.create(
            from_user=self.user2, to_profile=self.profile1, liked=True)

        result = user_is_matched(self.user1, self.user2)
        self.assertTrue(result)

    def test_user_is_matched_false_if_one_sided(self):
        MatchResponse.objects.create(
            from_user=self.user1, to_profile=self.profile2, liked=True)

        result = user_is_matched(self.user1, self.user2)
        self.assertFalse(result)

    def test_user_is_matched_false_if_profile_missing(self):
        self.profile2.delete()

        result = user_is_matched(self.user1, self.user2)
        self.assertFalse(result)


class LogoutAnd404ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='logoutuser', password='pass123'
        )
        self.client.login(username='logoutuser', password='pass123')

    def test_custom_logout_redirects_and_shows_message(self):
        response = self.client.get(reverse('custom_logout'), follow=True)

        # Check redirected to home
        self.assertRedirects(response, reverse('home'))

        # Check user is logged out
        self.assertNotIn('_auth_user_id', self.client.session)

        # Check success message
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any(
            "You have been logged out successfully."
            in str(m) for m in messages_list
        ))

    def test_custom_404_view_renders_404_template(self):
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
