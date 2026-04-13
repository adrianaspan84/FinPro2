from django.contrib import admin
from tinymce.widgets import TinyMCE
from django import forms
from .models import GalleryItem


class GalleryItemAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        required=False,
        label='Aprašymas / Turinys',
    )

    class Meta:
        model = GalleryItem
        fields = '__all__'


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    form = GalleryItemAdminForm
    list_display = ('id', 'title', 'media_type', 'order', 'is_published', 'uploaded_by', 'created_at')
    list_display_links = ('id', 'title')
    list_editable = ('order', 'is_published')
    list_filter = ('media_type', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('order', '-created_at')

    fieldsets = (
        ('Pagrindinė informacija', {
            'fields': ('title', 'media_type', 'order', 'is_published', 'uploaded_by'),
        }),
        ('Medija', {
            'fields': ('image', 'video_url', 'video_file'),
            'description': 'Pasirinkite vieną medijos tipą pagal "Medijos tipas" lauką.',
        }),
        ('Aprašymas (TinyMCE)', {
            'fields': ('content',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

