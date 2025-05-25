from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, ImageValidator, HouseImage, MatchResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.urls import reverse
from profiles.forms import UserForm, ProfileForm, ImageForm
from django.forms import modelformset_factory
from django.contrib.messages import get_messages


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass')
        self.profile = Profile.objects.create(
            user=self.user, location='Italy', is_visible=True)

    def test_profile_creation(self):
        self.assertEqual(self.profile.location, 'Italy')
        self.assertTrue(self.profile.is_visible)
        self.assertEqual(str(self.profile), f'{self.user.username} - Italy')


class ImageValidatorTest(TestCase):
    def setUp(self):
        self.validator = ImageValidator(max_size_mb=2)

    def test_valid_image(self):
        image = SimpleUploadedFile(
            "test.jpg", b"0" * 1024, content_type="image/jpeg")
        try:
            self.validator(image)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for a valid image.")

    def test_invalid_type(self):
        image = SimpleUploadedFile(
            "test.gif", b"0" * 1024, content_type="image/gif")
        with self.assertRaises(ValidationError) as cm:
            self.validator(image)
        self.assertIn("Only JPEG and PNG", str(cm.exception))

    def test_too_large_image(self):
        image = SimpleUploadedFile(
            "test.jpg", b"0" * 3 * 1024 * 1024, content_type="image/jpeg")
        with self.assertRaises(ValidationError) as cm:
            self.validator(image)
        self.assertIn("Maximum file size is", str(cm.exception))


class HouseImageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass123')
        self.profile = Profile.objects.create(user=self.user)

    def test_house_image_creation(self):
        image = SimpleUploadedFile(
            "house.jpg", b"0" * 1024, content_type="image/jpeg")
        house_image = HouseImage.objects.create(
            profile=self.profile, image=image, is_main=True)

        self.assertEqual(house_image.profile, self.profile)
        self.assertTrue(house_image.is_main)
        self.assertEqual(str(house_image), "Image for testuser")


class MatchResponseModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='testpass')
        self.user2 = User.objects.create_user(
            username='user2', password='testpass')
        self.profile2 = Profile.objects.create(user=self.user2)

    def test_create_match_response(self):
        response = MatchResponse.objects.create(
            from_user=self.user1,
            to_profile=self.profile2,
            liked=True
        )
        self.assertEqual(response.from_user, self.user1)
        self.assertEqual(response.to_profile, self.profile2)
        self.assertTrue(response.liked)

    def test_str_method(self):
        response = MatchResponse.objects.create(
            from_user=self.user1,
            to_profile=self.profile2,
            liked=False
        )
        self.assertEqual(str(response), "user1 disliked user2")

    def test_unique_together_constraint(self):
        MatchResponse.objects.create(
            from_user=self.user1,
            to_profile=self.profile2,
            liked=True
        )
        with self.assertRaises(Exception):  # Could be IntegrityError
            # or other depending on DB
            MatchResponse.objects.create(
                from_user=self.user1,
                to_profile=self.profile2,
                liked=False
            )


class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user, location="Spain")
        self.url = reverse('profile_view')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertIn('profile', response.context)
        self.assertEqual(response.context['profile'], self.profile)
        self.assertIn('house_images', response.context)
        self.assertIn('reviews', response.context)
        self.assertIn('average_rating', response.context)


class EditProfileViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user, location="Spain")
        self.url = reverse('edit_profile')  # Match your URL name exactly

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_get_request_renders_forms(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/edit_profile.html')
        self.assertIsInstance(response.context['user_form'], UserForm)
        self.assertIsInstance(response.context['profile_form'], ProfileForm)
        self.assertEqual(response.context['profile'], self.profile)

    def test_post_valid_data_updates_profile(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(self.url, {
            'username': 'testuser',     # required by UserForm
            'first_name': 'Updated',    # belongs to Profile or User, depending
            'last_name': 'Name',
            'bio': 'Test bio',          # required by ProfileForm
            'location': 'Updated Location',
        })

        # Expect redirect on success
        self.assertEqual(response.status_code, 302)

        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("updated" in str(m) for m in messages))


class SetMainImageViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user)

        dummy_file = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg")

        self.image1 = HouseImage.objects.create(
            profile=self.profile, image=dummy_file, is_main=False
        )
        self.image2 = HouseImage.objects.create(
            profile=self.profile, image=dummy_file, is_main=True
        )

        self.url = reverse('set_main_image', args=[self.image1.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_set_main_image(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)  # Redirect to edit_profile
        self.assertRedirects(response, reverse('edit_profile'))

        self.image1.refresh_from_db()
        self.image2.refresh_from_db()

        self.assertTrue(self.image1.is_main)
        self.assertFalse(self.image2.is_main)


class UploadImagesViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user)
        self.url = reverse('upload_images')
        self.ImageFormSet = modelformset_factory(
            HouseImage, form=ImageForm, extra=0)

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_upload_single_image_auto_sets_main(self):
        self.client.login(username='testuser', password='testpass')

        image_file = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )

        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-id': '',
            'form-0-image': '',
        }

        files = {
            'form-0-image': image_file,
        }

        response = self.client.post(
            self.url, data=data, files=files, follow=True)

        # Debug formset validation errors if test fails
        if response.context and 'formset' in response.context:
            for i, form in enumerate(response.context['formset'].forms):
                print(f"Form {i} errors:", form.errors)
            print(
                "Non-form errors:", response.context[
                    'formset'].non_form_errors())

        self.assertRedirects(response, reverse('edit_profile'))

        images = HouseImage.objects.filter(profile=self.profile)
        self.assertEqual(images.count(), 1)
        self.assertTrue(images.first().is_main)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("updated successfully" in str(m) for m in messages))

    def test_upload_sets_manual_main_image(self):
        self.client.login(username='testuser', password='testpass')

        image1 = HouseImage.objects.create(
            profile=self.profile,
            image=SimpleUploadedFile("a.jpg", b"a", content_type="image/jpeg"),
            is_main=False
        )
        image2 = HouseImage.objects.create(
            profile=self.profile,
            image=SimpleUploadedFile("b.jpg", b"b", content_type="image/jpeg"),
            is_main=False
        )

        form_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-0-id': image1.id,
            'form-1-id': image2.id,
            'main_image': str(image2.id),
        }

        response = self.client.post(self.url, data=form_data, follow=True)

        image1.refresh_from_db()
        image2.refresh_from_db()

        self.assertFalse(image1.is_main)
        self.assertTrue(image2.is_main)

        self.assertRedirects(response, reverse('edit_profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("updated successfully" in str(m) for m in messages))
