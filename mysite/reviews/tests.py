from django.test import TestCase

from .forms import ReviewForm


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
