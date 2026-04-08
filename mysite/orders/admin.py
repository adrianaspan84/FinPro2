from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'manager', 'status', 'created_at', 'deadline', 'is_overdue')
    list_filter = ('status', 'manager')
    search_fields = ('client__username', 'manager__username')
    inlines = [OrderItemInline]
