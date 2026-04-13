from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

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

	def test_gallery_pagination_exposes_three_page_blocks(self):
		for i in range(40):
			GalleryItem.objects.create(title=f'Item {i}', media_type='photo', is_published=True)

		response = self.client.get(reverse('gallery_home'), {'page': 4})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['page_numbers'], [4, 5])
		self.assertTrue(response.context['has_previous_block'])
		self.assertFalse(response.context['has_next_block'])
		self.assertEqual(response.context['previous_block_page'], 1)
		self.assertEqual(response.context['last_page'], 5)


class GalleryTikTokTests(TestCase):
	def test_tiktok_url_is_converted_to_embed_url(self):
		item = GalleryItem(
			title='TikTok test',
			media_type='tiktok_url',
			video_url='https://www.tiktok.com/@demo/video/7491234567890123456',
		)

		item.full_clean()
		self.assertEqual(item.embed_video_url, 'https://www.tiktok.com/embed/v3/7491234567890123456')

	def test_non_tiktok_url_is_rejected_for_tiktok_media_type(self):
		item = GalleryItem(
			title='Bad TikTok test',
			media_type='tiktok_url',
			video_url='https://www.youtube.com/watch?v=abc123',
		)

		with self.assertRaises(ValidationError):
			item.full_clean()

