from decimal import Decimal
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from services.models import Service, ServiceCategory


class EditOrderLinesTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client1', password='pass123')
        self.client_user.first_name = 'Jonas'
        self.client_user.last_name = 'Jonaitis'
        self.client_user.save()
        self.client_user.profile.role = 'client'
        self.client_user.profile.save()

        self.second_client_user = User.objects.create_user(username='client2', password='pass123')
        self.second_client_user.profile.role = 'client'
        self.second_client_user.profile.save()

        self.admin_user = User.objects.create_user(username='admin1', password='pass123')
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

        self.manager_user = User.objects.create_user(username='manager1', password='pass123')
        self.manager_user.profile.role = 'manager'
        self.manager_user.profile.save()

        self.other_manager_user = User.objects.create_user(username='manager2', password='pass123')
        self.other_manager_user.profile.role = 'manager'
        self.other_manager_user.profile.save()

        category = ServiceCategory.objects.create(name='Valymas')
        self.service_a = Service.objects.create(category=category, name='Langai', unit='vnt', price=Decimal('10.00'))
        self.service_b = Service.objects.create(category=category, name='Grindys', unit='m2', price=Decimal('5.00'))
        self.service_c = Service.objects.create(category=category, name='Sienos', unit='m2', price=Decimal('7.00'))

        self.order = Order.objects.create(
            client=self.client_user,
            manager=self.manager_user,
            status='new',
        )
        self.second_order = Order.objects.create(
            client=self.second_client_user,
            manager=self.manager_user,
            status='done',
        )
        OrderItem.objects.create(order=self.order, service=self.service_a, quantity=Decimal('2.00'))
        OrderItem.objects.create(order=self.order, service=self.service_b, quantity=Decimal('3.00'))
        OrderItem.objects.create(order=self.second_order, service=self.service_c, quantity=Decimal('1.00'))

    def test_edit_form_contains_existing_lines_json(self):
        self.client.login(username='manager1', password='pass123')

        response = self.client.get(reverse('edit_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('existing_items_json', response.context)
        existing = json.loads(response.context['existing_items_json'])
        self.assertEqual(len(existing), 2)
        self.assertTrue(any(line['service_id'] == self.service_a.id for line in existing))
        self.assertTrue(any(line['service_id'] == self.service_b.id for line in existing))
        self.assertEqual(len(response.context['existing_items_payload']), 2)

    def test_manager_can_replace_lines_update_price_quantity_and_remove(self):
        self.client.login(username='manager1', password='pass123')

        payload = [
            {
                'service_id': self.service_b.id,
                'quantity': '10.00',
                'price': '6.50',
                'name': self.service_b.name,
            },
            {
                'service_id': self.service_c.id,
                'quantity': '1.50',
                'price': '20.00',
                'name': self.service_c.name,
            },
        ]

        response = self.client.post(
            reverse('edit_order', args=[self.order.id]),
            data={
                'deadline': '',
                'status': 'in_progress',
                'manager_comment': 'Atnaujinta',
                'items_json': json.dumps(payload),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')
        self.assertEqual(self.order.manager_comment, 'Atnaujinta')

        items = list(self.order.items.select_related('service').order_by('service__name'))
        self.assertEqual(len(items), 2)
        self.assertEqual({item.service_id for item in items}, {self.service_b.id, self.service_c.id})

        by_service = {item.service_id: item for item in items}
        self.assertEqual(by_service[self.service_b.id].quantity, Decimal('10.00'))
        self.assertEqual(by_service[self.service_b.id].custom_price, Decimal('6.50'))
        self.assertEqual(by_service[self.service_c.id].quantity, Decimal('1.50'))
        self.assertEqual(by_service[self.service_c.id].custom_price, Decimal('20.00'))

    def test_other_manager_cannot_edit_foreign_order(self):
        self.client.login(username='manager2', password='pass123')

        response = self.client.get(reverse('edit_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 403)

    def test_manager_can_delete_owned_order(self):
        self.client.login(username='manager1', password='pass123')

        response = self.client.post(reverse('delete_order', args=[self.order.id]), data={'next': reverse('order_list')})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order_list'))
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_deleted)

    def test_admin_dashboard_shows_delete_actions(self):
        self.client.login(username='admin1', password='pass123')

        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('delete_order', args=[self.order.id]))

    def test_soft_deleted_order_not_visible_in_order_list(self):
        self.order.soft_delete()
        self.client.login(username='manager1', password='pass123')

        response = self.client.get(reverse('order_list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.order, response.context['orders'])

    def test_delete_is_post_only(self):
        self.client.login(username='manager1', password='pass123')

        response = self.client.get(reverse('delete_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Order.objects.filter(id=self.order.id, is_deleted=False).exists())

    def test_client_cannot_delete_order(self):
        self.client.login(username='client1', password='pass123')

        response = self.client.post(reverse('delete_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Order.objects.filter(id=self.order.id, is_deleted=False).exists())

    def test_admin_dashboard_can_show_deleted_orders_with_filter(self):
        self.order.soft_delete()
        self.client.login(username='admin1', password='pass123')

        response_without = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response_without.status_code, 200)
        self.assertFalse(response_without.context['include_deleted'])
        self.assertEqual(list(response_without.context['deleted_orders']), [])

        response_with = self.client.get(reverse('admin_dashboard'), {'include_deleted': '1'})
        self.assertEqual(response_with.status_code, 200)
        self.assertTrue(response_with.context['include_deleted'])
        self.assertIn(self.order, response_with.context['deleted_orders'])

    def test_admin_can_restore_soft_deleted_order(self):
        self.order.soft_delete()
        self.client.login(username='admin1', password='pass123')

        response = self.client.post(reverse('restore_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_deleted)
        self.assertIsNone(self.order.deleted_at)

    def test_non_admin_cannot_restore_soft_deleted_order(self):
        self.order.soft_delete()
        self.client.login(username='manager1', password='pass123')

        response = self.client.post(reverse('restore_order', args=[self.order.id]))

        self.assertEqual(response.status_code, 403)

    def test_admin_dashboard_search_and_status_filter(self):
        self.client.login(username='admin1', password='pass123')

        response = self.client.get(reverse('admin_dashboard'), {'q': 'client1', 'status': 'new'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.order, response.context['new_orders'])
        self.assertNotIn(self.second_order, response.context['done_orders'])

    def test_client_order_list_shows_only_view_and_invoice_actions(self):
        self.client.login(username='client1', password='pass123')

        response = self.client.get(reverse('order_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('order_detail', args=[self.order.id]))
        self.assertContains(response, reverse('download_invoice', args=[self.order.id]))
        self.assertNotContains(response, reverse('edit_order', args=[self.order.id]))
        self.assertNotContains(response, reverse('delete_order', args=[self.order.id]))


class OrderListPaginationTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client_pag', password='pass123')
        self.client_user.profile.role = 'client'
        self.client_user.profile.save()

        self.manager_user = User.objects.create_user(username='manager_pag', password='pass123')
        self.manager_user.profile.role = 'manager'
        self.manager_user.profile.save()

        category = ServiceCategory.objects.create(name='Paginacija')
        service = Service.objects.create(category=category, name='Paslauga', unit='vnt', price=Decimal('10.00'))

        for _ in range(12):
            order = Order.objects.create(client=self.client_user, manager=self.manager_user, status='new')
            OrderItem.objects.create(order=order, service=service, quantity=Decimal('1.00'))

    def test_order_list_paginates_for_client(self):
        self.client.login(username='client_pag', password='pass123')

        response = self.client.get(reverse('order_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)
        self.assertEqual(len(response.context['orders']), 10)


