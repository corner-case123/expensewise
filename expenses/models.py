from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Expense category with color coding for charts."""

    DEFAULT_CATEGORIES = [
        ('Food & Dining', '#FF6384'),
        ('Transportation', '#36A2EB'),
        ('Housing & Rent', '#FFCE56'),
        ('Utilities', '#4BC0C0'),
        ('Entertainment', '#9966FF'),
        ('Healthcare', '#FF9F40'),
        ('Shopping', '#C9CBCF'),
        ('Education', '#7BC67E'),
        ('Travel', '#F67019'),
        ('Other', '#8B8B8B'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
    )
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text='Hex color code for charts (e.g., #FF6384)',
    )
    icon = models.CharField(
        max_length=50,
        default='bi-tag',
        help_text='Bootstrap icon class',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name

    @classmethod
    def create_defaults_for_user(cls, user):
        """Create default categories for a new user."""
        icons = [
            'bi-egg-fried', 'bi-car-front', 'bi-house', 'bi-lightning',
            'bi-controller', 'bi-heart-pulse', 'bi-bag', 'bi-book',
            'bi-airplane', 'bi-three-dots',
        ]
        for (name, color), icon in zip(cls.DEFAULT_CATEGORIES, icons):
            cls.objects.get_or_create(
                user=user,
                name=name,
                defaults={'color': color, 'icon': icon},
            )


class Expense(models.Model):
    """Individual expense record linked to a user and category."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} — ${self.amount}"


class Budget(models.Model):
    """Monthly budget limit for a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
    )
    month = models.PositiveIntegerField(
        help_text='Month number (1-12)',
    )
    year = models.PositiveIntegerField(
        help_text='Year (e.g., 2024)',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Budget {self.month}/{self.year}: ${self.amount}"
