from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import ReviewForm
from .models import Review


class ReviewFormValidationTests(TestCase):
    def test_accepts_rating_and_content(self):
        form = ReviewForm(data={'rating': 5, 'content': 'Puikus aptarnavimas.'})
        self.assertTrue(form.is_valid())

    def test_rejects_empty_content(self):
        form = ReviewForm(data={'rating': 5, 'content': '   '})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_has_only_required_fields(self):
        form = ReviewForm()
        self.assertEqual(list(form.fields.keys()), ['rating', 'content'])


class ReviewCrudCbvTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='review_client', password='pass123')
        self.client_user.profile.role = 'client'
        self.client_user.profile.save()

        self.manager_user = User.objects.create_user(username='review_manager', password='pass123')
        self.manager_user.profile.role = 'manager'
        self.manager_user.profile.save()

        self.admin_user = User.objects.create_user(username='review_admin', password='pass123', is_staff=True)
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_client_can_create_review_via_createview(self):
        self.client.login(username='review_client', password='pass123')

        response = self.client.post(reverse('reviews_create'), {'rating': 5, 'content': 'CBV create'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(user=self.client_user, content='CBV create').exists())

    def test_non_client_cannot_create_review(self):
        self.client.login(username='review_manager', password='pass123')

        response = self.client.post(reverse('reviews_create'), {'rating': 5, 'content': 'Denied'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(user=self.manager_user, content='Denied').exists())

    def test_only_admin_can_edit_and_delete(self):
        review = Review.objects.create(user=self.client_user, rating=5, content='To edit', is_approved=True)

        self.client.login(username='review_manager', password='pass123')
        deny_edit = self.client.get(reverse('reviews_edit', args=[review.id]))
        self.assertEqual(deny_edit.status_code, 302)

        self.client.logout()
        self.client.login(username='review_admin', password='pass123')

        allow_edit = self.client.get(reverse('reviews_edit', args=[review.id]))
        self.assertEqual(allow_edit.status_code, 200)

        delete_get = self.client.get(reverse('reviews_delete', args=[review.id]))
        self.assertEqual(delete_get.status_code, 302)

        delete_post = self.client.post(reverse('reviews_delete', args=[review.id]))
        self.assertEqual(delete_post.status_code, 302)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

