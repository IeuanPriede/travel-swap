from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from profiles.models import Profile, HouseImage, MatchResponse
from django.core.exceptions import ValidationError
import io
from PIL import Image
from profiles.forms import (
    CustomUserCreationForm,
    UserForm,
    ProfileForm,
    ImageForm,
    ContactForm
)
from django.urls import reverse


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
        self.assertRedirects(response, '/accounts/login/?next=/profiles/')


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
