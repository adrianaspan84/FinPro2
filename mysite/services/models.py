from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _("Paslaugų kategorija")
        verbose_name_plural = _("Paslaugų kategorijos")
        ordering = ['id']

    def __str__(self):
        return self.name


class Service(models.Model):
    UNIT_CHOICES = [
        ('m2', 'm²'),
        ('m', _('bėginiai metrai')),
        ('vnt', _('vnt.')),
        ('h', _('valandos')),
        ('task', _('taškai')),
    ]

    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='vnt')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Paslauga")
        verbose_name_plural = _("Paslaugos")
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"
