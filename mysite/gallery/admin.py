from django.contrib import admin
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
