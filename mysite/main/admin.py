from django.contrib import admin
from .models import Profile, SiteSettings


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city')
    list_filter = ('role', 'city')
    search_fields = ('user__username', 'phone', 'city')


class SiteSettingsAdmin(admin.ModelAdmin):
    fields = ('background_image',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)

