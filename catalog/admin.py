from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'price', 'stock')
    search_fields = ('sku', 'name')
    prepopulated_fields = {'slug': ('name',)}
