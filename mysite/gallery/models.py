from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from django.core.exceptions import ValidationError
from urllib.parse import urlparse


class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', _('Nuotrauka')),
        ('video_url', _('Video nuoroda (YouTube/Vimeo)')),
        ('tiktok_url', _('TikTok video nuoroda')),
        ('video_file', _('Video failas')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('Pavadinimas'))
    media_type = models.CharField(
        max_length=20, choices=MEDIA_TYPE_CHOICES, default='photo',
        verbose_name=_('Medijos tipas')
    )
    image = models.ImageField(
        upload_to='gallery/', blank=True, null=True,
        verbose_name=_('Nuotrauka')
    )
    video_url = models.URLField(
        blank=True, null=True,
        verbose_name=_('Video nuoroda'),
        help_text=_('YouTube, Vimeo arba TikTok nuoroda (pagal pasirinktą medijos tipą)')
    )
    video_file = models.FileField(
        upload_to='gallery/videos/', blank=True, null=True,
        verbose_name=_('Video failas')
    )
    content = HTMLField(blank=True, verbose_name=_('Aprašymas / Turinys'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Eilės tvarka'))
    is_published = models.BooleanField(default=True, verbose_name=_('Viešas'))
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('Įkėlė')
    )

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _('Galerijos įrašas')
        verbose_name_plural = _('Galerija')

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.media_type == 'photo' and not self.image:
            raise ValidationError({'image': _('Pasirinkus nuotrauką, reikia įkelti paveikslėlį.')})

        if self.media_type == 'video_file' and not self.video_file:
            raise ValidationError({'video_file': _('Pasirinkus video failą, reikia įkelti failą.')})

        if self.media_type in {'video_url', 'tiktok_url'}:
            if not self.video_url:
                raise ValidationError({'video_url': _('Pasirinkus video nuorodą, reikia įvesti nuorodą.')})

            parsed = urlparse(self.video_url)
            host = parsed.netloc.lower()

            if self.media_type == 'video_url':
                allowed_hosts = {
                    'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com',
                    'vimeo.com', 'www.vimeo.com', 'player.vimeo.com',
                }
                if host not in allowed_hosts:
                    raise ValidationError({'video_url': _('Leidžiamos tik YouTube arba Vimeo nuorodos.')})

            if self.media_type == 'tiktok_url':
                allowed_hosts = {'tiktok.com', 'www.tiktok.com', 'm.tiktok.com'}
                if host not in allowed_hosts:
                    raise ValidationError({'video_url': _('Leidžiamos tik TikTok nuorodos.')})
                if '/video/' not in parsed.path and '/embed/' not in parsed.path:
                    raise ValidationError({'video_url': _('Naudokite pilną TikTok video nuorodą.')})

    @property
    def embed_video_url(self):
        if not self.video_url:
            return ''

        parsed = urlparse(self.video_url)
        host = parsed.netloc.lower()

        if self.media_type == 'tiktok_url':
            if '/embed/' in parsed.path:
                return self.video_url

            parts = [part for part in parsed.path.split('/') if part]
            if 'video' in parts:
                video_index = parts.index('video')
                if video_index + 1 < len(parts):
                    video_id = parts[video_index + 1]
                    return f'https://www.tiktok.com/embed/v3/{video_id}'
            return self.video_url

        return self.video_url

