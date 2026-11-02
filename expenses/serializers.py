from rest_framework import serializers
from .models import Expense, Category, Budget


class CategorySerializer(serializers.ModelSerializer):
    expense_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'icon', 'expense_count', 'created_at']
        read_only_fields = ['created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )

    class Meta:
        model = Expense
        fields = [
            'id', 'category', 'category_name', 'amount',
            'description', 'notes', 'date', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'month', 'year', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MonthlySummarySerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    expense_count = serializers.IntegerField()
    budget_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    category_breakdown = serializers.ListField()
