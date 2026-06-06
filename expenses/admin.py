from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type']
    list_filter = ['category_type']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'date', 'description']
    list_filter = ['category', 'date']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'