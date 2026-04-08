from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Paslaugų kategorija"
        verbose_name_plural = "Paslaugų kategorijos"
        ordering = ['id']

    def __str__(self):
        return self.name


class Service(models.Model):
    UNIT_CHOICES = [
        ('m2', 'm²'),
        ('m', 'bėginiai metrai'),
        ('vnt', 'vnt.'),
        ('h', 'valandos'),
        ('task', 'taškai'),
    ]

    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='vnt')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Paslauga"
        verbose_name_plural = "Paslaugos"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"
