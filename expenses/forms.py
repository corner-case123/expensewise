from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Expense, Category, Budget


class CustomUserCreationForm(UserCreationForm):
    """Extended user registration form with email field."""

    email = forms.EmailField(required=True, help_text='Required.')
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ExpenseForm(forms.ModelForm):
    """Form for creating and editing expenses."""

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )

    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date', 'notes']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': '0.00',
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g., Lunch at restaurant',
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Optional notes...',
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user
            )


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""

    class Meta:
        model = Category
        fields = ['name', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Category name',
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-color',
                    'type': 'color',
                }
            ),
            'icon': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    ('bi-tag', '🏷️ Tag'),
                    ('bi-egg-fried', '🍳 Food'),
                    ('bi-car-front', '🚗 Transport'),
                    ('bi-house', '🏠 Housing'),
                    ('bi-lightning', '⚡ Utilities'),
                    ('bi-controller', '🎮 Entertainment'),
                    ('bi-heart-pulse', '❤️ Healthcare'),
                    ('bi-bag', '🛍️ Shopping'),
                    ('bi-book', '📚 Education'),
                    ('bi-airplane', '✈️ Travel'),
                    ('bi-three-dots', '⋯ Other'),
                    ('bi-gift', '🎁 Gifts'),
                    ('bi-tools', '🔧 Maintenance'),
                    ('bi-phone', '📱 Phone'),
                    ('bi-wifi', '📶 Internet'),
                ],
            ),
        }


class BudgetForm(forms.ModelForm):
    """Form for setting monthly budget."""

    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Budget
        fields = ['month', 'year', 'amount']
        widgets = {
            'year': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '2020',
                    'max': '2030',
                }
            ),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': '0.00',
                }
            ),
        }


class ExpenseFilterForm(forms.Form):
    """Form for filtering expenses on the list page."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Search description...',
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user
            )
