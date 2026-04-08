from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Atsiliepimas"
        verbose_name_plural = "Atsiliepimai"

    def __str__(self):
        return f"Atsiliepimas #{self.id} — {self.user.username}"

    @property
    def short_comment(self):
        return self.comment[:50] + "..." if len(self.comment) > 50 else self.comment
