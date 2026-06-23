from django.contrib import admin

from orders.models import Order


@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ("client", "status", "created_at", "total_amount")
    list_filter = ("created_at", "total_amount")
    search_fields = ("client",)