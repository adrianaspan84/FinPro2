from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from services.models import Service
from decimal import Decimal, ROUND_HALF_UP


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', _('Naujas')),
        ('in_progress', _('Vykdomas')),
        ('done', _('Atliktas')),
        ('cancelled', _('Atšauktas')),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_orders')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    manager_comment = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Užsakymas")
        verbose_name_plural = _("Užsakymai")

    def __str__(self):
        return f"Užsakymas #{self.id} ({self.client.username})"

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def is_overdue(self):
        if self.deadline and self.status != 'done':
            return timezone.now().date() > self.deadline
        return False

    @property
    def overdue_days(self):
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.deadline).days

    @property
    def subtotal(self):
        raw_total = sum(item.total_price for item in self.items.all())
        return self._money(raw_total)

    @property
    def vat_amount(self):
        return self._money(self.subtotal * Decimal('0.21'))

    @property
    def total_with_vat(self):
        return self._money(self.subtotal + self.vat_amount)

    @property
    def total_price(self):
        # Backward-compatible alias used in list/detail templates.
        return self.total_with_vat

    def assign_manager(self):
        """Automatinis vadybininko priskyrimas pagal mažiausią aktyvių užsakymų skaičių."""
        managers = User.objects.filter(profile__role='manager')
        if managers.exists():
            manager = sorted(
                managers,
                key=lambda m: m.managed_orders.filter(
                    status__in=['new', 'in_progress'],
                    is_deleted=False,
                ).count(),
            )[0]
            self.manager = manager
            self.save()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _("Užsakymo eilutė")
        verbose_name_plural = _("Užsakymo eilutės")

    @property
    def unit_price(self):
        """Returns custom price if set, otherwise the service default price."""
        return self.custom_price if self.custom_price is not None else self.service.price

    @property
    def total_price(self):
        raw_total = self.unit_price * self.quantity
        return Order._money(raw_total)

    def __str__(self):
        return f"{self.service.name} x {self.quantity}"
