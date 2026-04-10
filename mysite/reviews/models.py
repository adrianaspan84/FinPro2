from urllib.parse import urlparse
import os

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

MAX_REVIEW_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
YOUTUBE_HOSTS = {'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)
    content = HTMLField(blank=True, verbose_name=_('Atsiliepimo tekstas'))

    photo = models.ImageField(upload_to='reviews/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, verbose_name=_('Video nuoroda'))
    video_file = models.FileField(upload_to='reviews/videos/', blank=True, null=True, verbose_name=_('Video failas'))

    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Atsiliepimas")
        verbose_name_plural = _("Atsiliepimai")

    def __str__(self):
        return f"Atsiliepimas #{self.id} - {self.user.username}"

    def clean(self):
        if self.photo:
            if getattr(self.photo, 'size', 0) > MAX_REVIEW_IMAGE_SIZE:
                raise ValidationError({'photo': _('Nuotrauka per didelė. Maksimalus dydis: 2 MB.')})

            ext = os.path.splitext(self.photo.name.lower())[1]
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError({'photo': _('Leidžiami tik JPG arba PNG failai.')})

        if self.video_file:
            raise ValidationError({'video_file': _('Video failo kelti negalima. Naudokite YouTube nuorodą.')})

        if self.video_url:
            host = urlparse(self.video_url).netloc.lower()
            if host not in YOUTUBE_HOSTS:
                raise ValidationError({'video_url': _('Leidžiamos tik YouTube nuorodos.')})
