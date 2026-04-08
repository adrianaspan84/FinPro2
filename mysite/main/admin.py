from django.contrib import admin



class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city')
    list_filter = ('role', 'city')
    search_fields = ('user__username', 'phone', 'city')
