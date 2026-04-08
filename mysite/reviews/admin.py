from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved')
    search_fields = ('user__username', 'comment')
    list_editable = ('is_approved',)
