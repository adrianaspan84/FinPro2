from django.test import TestCase
from django.urls import reverse

from .models import GalleryItem


class GalleryPaginationTests(TestCase):
	def test_gallery_home_paginates_items(self):
		for i in range(12):
			GalleryItem.objects.create(title=f'Item {i}', media_type='photo', is_published=True)

		response = self.client.get(reverse('gallery_home'))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['is_paginated'])
		self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)
		self.assertEqual(len(response.context['items']), 9)
