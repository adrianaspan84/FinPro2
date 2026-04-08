from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from services.models import Service
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Naujas'),
        ('in_progress', 'Vykdomas'),
        ('done', 'Atliktas'),
        ('cancelled', 'Atšauktas'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_orders')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Užsakymas"
        verbose_name_plural = "Užsakymai"

    def __str__(self):
        return f"Užsakymas #{self.id} ({self.client.username})"

    @property
    def is_overdue(self):
        if self.deadline and self.status != 'done':
            return timezone.now().date() > self.deadline
        return False

    @property
    def subtotal(self):
        total = sum(item.total_price for item in self.items.all())
        return total

    @property
    def vat_amount(self):
        return self.subtotal * Decimal('0.21')

    @property
    def total_with_vat(self):
        return self.subtotal + self.vat_amount

    def assign_manager(self):
        """Automatinis vadibininko priskyrimas pagal mažiausią aktyvių užsakymų skaičių."""
        managers = User.objects.filter(profile__role='manager')
        if managers.exists():
            manager = sorted(managers, key=lambda m: m.managed_orders.filter(status__in=['new', 'in_progress']).count())[0]
            self.manager = manager
            self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        verbose_name = "Užsakymo eilutė"
        verbose_name_plural = "Užsakymo eilutės"

    @property
    def total_price(self):
        return self.service.price * self.quantity

    def __str__(self):
        return f"{self.service.name} x {self.quantity}"
