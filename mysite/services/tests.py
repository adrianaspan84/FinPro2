
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from services.models import Service, ServiceCategory


class ServicesAccordionTests(TestCase):
    def test_services_home_renders_collapsible_groups(self):
        category = ServiceCategory.objects.create(name='Langai')
        Service.objects.create(category=category, name='Valymas', unit='vnt', price=Decimal('25.00'))

        response = self.client.get(reverse('services_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-bs-toggle="collapse"')
        self.assertContains(response, f'categoryCollapse{category.id}')
        self.assertContains(response, 'class="collapse"')
        self.assertContains(response, 'Valymas')
