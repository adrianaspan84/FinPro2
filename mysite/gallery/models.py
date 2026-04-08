from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='gallery/')
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Galerijos nuotrauka"
        verbose_name_plural = "Galerijos nuotraukos"

    def __str__(self):
        return self.title
