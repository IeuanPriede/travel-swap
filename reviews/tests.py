from django.test import TestCase, Client
from django.contrib.auth.models import User
from reviews.models import Review
from django.db import IntegrityError
from django.urls import reverse
from profiles.models import MatchResponse, Profile
from reviews.forms import ReviewForm


class ReviewModelTest(TestCase):

    def setUp(self):
        self.reviewer = User.objects.create_user(
            username='alice', password='pass123')
        self.reviewee = User.objects.create_user(
            username='bob', password='pass123')

    def test_create_review(self):
        review = Review.objects.create(
            reviewer=self.reviewer,
            reviewee=self.reviewee,
            rating=5,
            comment="Excellent experience!"
        )

        self.assertEqual(review.reviewer, self.reviewer)
        self.assertEqual(review.reviewee, self.reviewee)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent experience!")
        self.assertIsNotNone(review.created_at)

        expected_str = (
            f"{self.reviewer} → {self.reviewee} ({review.rating} stars)"
        )
        self.assertEqual(str(review), expected_str)

    def test_unique_reviewer_reviewee_constraint(self):
        Review.objects.create(
            reviewer=self.reviewer,
            reviewee=self.reviewee,
            rating=4,
            comment="Great!"
        )

        with self.assertRaises(IntegrityError):
            Review.objects.create(
                reviewer=self.reviewer,
                reviewee=self.reviewee,
                rating=2,
                comment="Second review should fail"
            )


class ReviewViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.reviewer = User.objects.create_user(
            username='alice', password='pass123')
        self.reviewee = User.objects.create_user(
            username='bob', password='pass123')

        # Create dummy profiles (needed for MatchResponse and view logic)
        self.reviewer_profile = Profile.objects.create(
            user=self.reviewer, location="A")
        self.reviewee_profile = Profile.objects.create(
            user=self.reviewee, location="B")

        # Mutual like = matched
        MatchResponse.objects.create(
            from_user=self.reviewer,
            to_profile=self.reviewee_profile,
            liked=True
        )
        MatchResponse.objects.create(
            from_user=self.reviewee,
            to_profile=self.reviewer_profile,
            liked=True
        )

    def test_leave_review_post_valid(self):
        self.client.login(username='alice', password='pass123')
        url = reverse('leave_review', args=[self.reviewee.id])
        response = self.client.post(url, {
            'rating': 4,
            'comment': 'Lovely host!'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Review.objects.filter(
                reviewer=self.reviewer, reviewee=self.reviewee).exists())

    def test_cannot_review_self(self):
        self.client.login(username='alice', password='pass123')
        url = reverse('leave_review', args=[self.reviewer.id])
        response = self.client.get(url, follow=True)
        self.assertContains(response, "You cannot review yourself.")

    def test_cannot_review_unmatched_user(self):
        # remove match
        MatchResponse.objects.all().delete()
        self.client.login(username='alice', password='pass123')
        url = reverse('leave_review', args=[self.reviewee.id])
        response = self.client.get(url, follow=True)
        self.assertContains(response, "You can only review matched users.")

    def test_delete_review(self):
        Review.objects.create(
            reviewer=self.reviewer,
            reviewee=self.reviewee,
            rating=5,
            comment="Great!"
        )
        self.client.login(username='alice', password='pass123')
        url = reverse('delete_review', args=[self.reviewee.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Review.objects.filter(
                reviewer=self.reviewer,
                reviewee=self.reviewee
            ).exists()
        )


class ReviewFormTest(TestCase):

    def test_form_valid_data(self):
        form = ReviewForm(data={
            'rating': 4,
            'comment': 'Great host, very welcoming!'
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_rating(self):
        form = ReviewForm(data={
            'comment': 'Lovely stay!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_form_missing_comment(self):
        form = ReviewForm(data={
            'rating': 5,
            'comment': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_form_rating_choices(self):
        form = ReviewForm()
        choices = list(form.fields['rating'].choices)
        expected_choices = [('', '---------')] + [(i, i) for i in range(1, 6)]
        self.assertEqual(choices, expected_choices)

    def test_form_labels(self):
        form = ReviewForm()
        self.assertEqual(form.fields['rating'].label, 'Star Rating')
        self.assertEqual(form.fields['comment'].label, 'Your Review')
