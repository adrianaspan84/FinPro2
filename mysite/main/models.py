from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    ROLE_CHOICES = [
        ('client', _('Klientas')),
        ('manager', _('Vadybininkas')),
        ('admin', _('Administratorius')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    # Juridinio asmens rekvizitai (naudojami sąskaitose)
    is_legal_entity = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True)
    company_code = models.CharField(max_length=30, blank=True)
    company_vat_code = models.CharField(max_length=30, blank=True)
    company_address = models.CharField(max_length=255, blank=True)

    @property
    def billing_name(self):
        if self.is_legal_entity and self.company_name:
            return self.company_name
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name or self.user.username

    @property
    def billing_address(self):
        if self.is_legal_entity and self.company_address:
            return self.company_address
        if self.address and self.city:
            return f"{self.address}, {self.city}"
        return self.address or self.city or ''

    def __str__(self):
        return f"{self.user.username} profilis"
