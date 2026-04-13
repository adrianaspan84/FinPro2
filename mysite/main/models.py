from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

ROTATING_BACKGROUND_DIR = 'settings/rotating'
ROTATING_BACKGROUND_SLOTS = 5
ROTATING_BACKGROUND_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
ROTATING_CONFIG_PATH = f'{ROTATING_BACKGROUND_DIR}/rotation_config.json'
DEFAULT_ROTATION_SECONDS = 30


def get_rotating_background_urls():
    urls = []
    for slot in range(1, ROTATING_BACKGROUND_SLOTS + 1):
        for ext in ROTATING_BACKGROUND_EXTENSIONS:
            path = f'{ROTATING_BACKGROUND_DIR}/background_{slot}{ext}'
            if default_storage.exists(path):
                urls.append(default_storage.url(path))
                break
    return urls


def save_rotating_background(slot, uploaded_file):
    if not uploaded_file or slot < 1 or slot > ROTATING_BACKGROUND_SLOTS:
        return

    # Keep one file per slot by removing previous known extensions first.
    for ext in ROTATING_BACKGROUND_EXTENSIONS:
        old_path = f'{ROTATING_BACKGROUND_DIR}/background_{slot}{ext}'
        if default_storage.exists(old_path):
            default_storage.delete(old_path)

    extension = ''
    if '.' in uploaded_file.name:
        extension = '.' + uploaded_file.name.rsplit('.', 1)[1].lower()
    if extension not in ROTATING_BACKGROUND_EXTENSIONS:
        extension = '.jpg'

    target_path = f'{ROTATING_BACKGROUND_DIR}/background_{slot}{extension}'
    default_storage.save(target_path, uploaded_file)


def get_hero_rotation_settings():
    settings = {
        'enabled': True,
        'interval_seconds': DEFAULT_ROTATION_SECONDS,
    }
    if not default_storage.exists(ROTATING_CONFIG_PATH):
        return settings

    try:
        with default_storage.open(ROTATING_CONFIG_PATH, 'r') as config_file:
            data = json.load(config_file)
        settings['enabled'] = bool(data.get('enabled', True))
        interval = int(data.get('interval_seconds', DEFAULT_ROTATION_SECONDS))
        settings['interval_seconds'] = max(5, min(600, interval))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return settings
    return settings


def save_hero_rotation_settings(enabled, interval_seconds):
    interval = max(5, min(600, int(interval_seconds or DEFAULT_ROTATION_SECONDS)))
    payload = {
        'enabled': bool(enabled),
        'interval_seconds': interval,
    }
    if default_storage.exists(ROTATING_CONFIG_PATH):
        default_storage.delete(ROTATING_CONFIG_PATH)
    default_storage.save(
        ROTATING_CONFIG_PATH,
        ContentFile(json.dumps(payload, ensure_ascii=False, indent=2)),
    )

class Profile(models.Model):
    ROLE_CHOICES = [
        ('client', _('Klientas')),
        ('manager', _('Vadybininkas')),
        ('admin', _('Administratorius')),
        ('staff', _('Darbuotojas')),
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


class SiteSettings(models.Model):
    """Site-wide configuration settings."""

    background_image = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        help_text='Homepage hero section background image'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    @classmethod
    def load(cls):
        """Get or create singleton settings instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

