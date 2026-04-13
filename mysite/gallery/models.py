from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField


class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', _('Nuotrauka')),
        ('video_url', _('Video nuoroda (YouTube/Vimeo)')),
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
        help_text=_('YouTube arba Vimeo nuoroda (pvz. https://www.youtube.com/embed/XXX)')
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

