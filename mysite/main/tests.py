from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class NavbarOrderLinkTests(TestCase):
	def setUp(self):
		self.client_user = User.objects.create_user(username='client_nav', password='pass123')
		self.client_user.profile.role = 'client'
		self.client_user.profile.save()

		self.admin_user = User.objects.create_user(username='admin_nav', password='pass123')
		self.admin_user.profile.role = 'admin'
		self.admin_user.profile.save()

	def test_client_sees_mano_uzsakymai_link(self):
		self.client.login(username='client_nav', password='pass123')

		response = self.client.get(reverse('order_list'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Mano užsakymai')

	def test_admin_does_not_see_mano_uzsakymai_link(self):
		self.client.login(username='admin_nav', password='pass123')

		response = self.client.get(reverse('admin_dashboard'))

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'Mano užsakymai')
