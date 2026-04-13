from django.contrib import admin
from django import forms
from django.utils.html import format_html_join

from .models import (
    Profile,
    SiteSettings,
    get_rotating_background_urls,
    save_rotating_background,
    get_hero_rotation_settings,
    save_hero_rotation_settings,
)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city')
    list_filter = ('role', 'city')
    search_fields = ('user__username', 'phone', 'city')


class SiteSettingsAdmin(admin.ModelAdmin):
    class SiteSettingsForm(forms.ModelForm):
        hero_rotation_enabled = forms.BooleanField(required=False, initial=True, label='Fono rotacija įjungta')
        hero_rotation_seconds = forms.IntegerField(required=True, initial=30, min_value=5, max_value=600, label='Fono keitimo intervalas (sek.)')
        background_image_1 = forms.ImageField(required=False, label='Fono nuotrauka #1')
        background_image_2 = forms.ImageField(required=False, label='Fono nuotrauka #2')
        background_image_3 = forms.ImageField(required=False, label='Fono nuotrauka #3')
        background_image_4 = forms.ImageField(required=False, label='Fono nuotrauka #4')
        background_image_5 = forms.ImageField(required=False, label='Fono nuotrauka #5')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            rotation_settings = get_hero_rotation_settings()
            self.fields['hero_rotation_enabled'].initial = rotation_settings['enabled']
            self.fields['hero_rotation_seconds'].initial = rotation_settings['interval_seconds']

        class Meta:
            model = SiteSettings
            fields = '__all__'

    form = SiteSettingsForm
    fields = (
        'background_image',
        'hero_rotation_enabled',
        'hero_rotation_seconds',
        'background_image_1',
        'background_image_2',
        'background_image_3',
        'background_image_4',
        'background_image_5',
        'rotating_background_preview',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('rotating_background_preview', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        save_hero_rotation_settings(
            enabled=form.cleaned_data.get('hero_rotation_enabled', True),
            interval_seconds=form.cleaned_data.get('hero_rotation_seconds', 30),
        )
        for slot in range(1, 6):
            uploaded = form.cleaned_data.get(f'background_image_{slot}')
            if uploaded:
                save_rotating_background(slot, uploaded)

    @admin.display(description='Aktyvios fono nuotraukos (rotacija)')
    def rotating_background_preview(self, _obj):
        urls = get_rotating_background_urls()
        if not urls:
            return 'Nėra įkeltų rotacijos fonų (naudojamas pagrindinis fonas).'

        items = format_html_join(
            '',
            '<div style="margin:0 12px 12px 0;display:inline-block;text-align:center;">'
            '<img src="{}" style="width:140px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #cbd5e1;display:block;" />'
            '<small>#{} </small>'
            '</div>',
            ((url, idx) for idx, url in enumerate(urls, start=1)),
        )
        return items


admin.site.register(Profile, ProfileAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)

