from django.contrib import admin
from .models import Category, Expense, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'icon', 'created_at']
    list_filter = ['user']
    search_fields = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'description', 'amount', 'category', 'date', 'user', 'created_at',
    ]
    list_filter = ['category', 'date', 'user']
    search_fields = ['description', 'notes']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'year', 'amount']
    list_filter = ['year', 'month', 'user']
