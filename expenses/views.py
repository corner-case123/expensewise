import csv
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View

from .forms import (
    CustomUserCreationForm, ExpenseForm, CategoryForm,
    BudgetForm, ExpenseFilterForm,
)
from .models import Expense, Category, Budget


# ─── Authentication ──────────────────────────────────────────────

def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Category.create_defaults_for_user(user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# ─── Dashboard ───────────────────────────────────────────────────

@login_required
def dashboard(request):
    """Main dashboard with monthly summary and charts."""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Get expenses for current month
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year,
    )

    # Total spent this month
    total_spent = monthly_expenses.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    # Category breakdown for pie chart
    category_data = (
        monthly_expenses
        .values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Daily spending for line chart
    daily_data = (
        monthly_expenses
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    # Budget info
    budget = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year,
    ).first()

    budget_percentage = 0
    if budget and budget.amount > 0:
        budget_percentage = min(
            round((total_spent / budget.amount) * 100, 1), 100
        )

    # Recent expenses
    recent_expenses = monthly_expenses[:5]

    # Expense count
    expense_count = monthly_expenses.count()

    # Average daily spending
    days_passed = today.day
    avg_daily = (
        total_spent / days_passed if days_passed > 0 else Decimal('0.00')
    )

    context = {
        'total_spent': total_spent,
        'expense_count': expense_count,
        'avg_daily': avg_daily,
        'budget': budget,
        'budget_percentage': budget_percentage,
        'remaining_budget': (
            budget.amount - total_spent if budget else None
        ),
        'category_labels': [
            item['category__name'] or 'Uncategorized'
            for item in category_data
        ],
        'category_amounts': [
            float(item['total']) for item in category_data
        ],
        'category_colors': [
            item['category__color'] or '#8B8B8B'
            for item in category_data
        ],
        'daily_labels': [
            item['day'].strftime('%b %d') for item in daily_data
        ],
        'daily_amounts': [
            float(item['total']) for item in daily_data
        ],
        'recent_expenses': recent_expenses,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'expenses/dashboard.html', context)


# ─── Expenses CRUD ───────────────────────────────────────────────

@login_required
def expense_list(request):
    """List expenses with filtering and search."""
    expenses = Expense.objects.filter(user=request.user).select_related('category')

    filter_form = ExpenseFilterForm(request.GET, user=request.user)

    if filter_form.is_valid():
        category = filter_form.cleaned_data.get('category')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        search = filter_form.cleaned_data.get('search')

        if category:
            expenses = expenses.filter(category=category)
        if date_from:
            expenses = expenses.filter(date__gte=date_from)
        if date_to:
            expenses = expenses.filter(date__lte=date_to)
        if search:
            expenses = expenses.filter(description__icontains=search)

    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'expenses': expenses,
        'filter_form': filter_form,
        'total': total,
        'count': expenses.count(),
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create(request):
    """Create a new expense."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Add Expense',
    })


@login_required
def expense_edit(request, pk):
    """Edit an existing expense."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Edit Expense',
        'expense': expense,
    })


@login_required
def expense_delete(request, pk):
    """Delete an expense."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')

    return render(request, 'expenses/expense_confirm_delete.html', {
        'expense': expense,
    })


# ─── Categories ──────────────────────────────────────────────────

@login_required
def category_list(request):
    """List and manage categories."""
    categories = Category.objects.filter(user=request.user).annotate(
        expense_count=Count('expenses'),
        total_spent=Sum('expenses__amount'),
    )
    return render(request, 'expenses/category_list.html', {
        'categories': categories,
    })


@login_required
def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'expenses/category_form.html', {
        'form': form,
        'title': 'Add Category',
    })


@login_required
def category_edit(request, pk):
    """Edit a category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'expenses/category_form.html', {
        'form': form,
        'title': 'Edit Category',
    })


@login_required
def category_delete(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted!')
        return redirect('category_list')

    return render(request, 'expenses/category_confirm_delete.html', {
        'category': category,
    })


# ─── Budget ──────────────────────────────────────────────────────

@login_required
def budget_set(request):
    """Set or update monthly budget."""
    today = timezone.now().date()
    budget = Budget.objects.filter(
        user=request.user,
        month=today.month,
        year=today.year,
    ).first()

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget_obj = form.save(commit=False)
            budget_obj.user = request.user
            budget_obj.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('dashboard')
    else:
        initial = {'month': today.month, 'year': today.year}
        form = BudgetForm(instance=budget, initial=initial if not budget else None)

    return render(request, 'expenses/budget_form.html', {
        'form': form,
        'budget': budget,
    })


# ─── CSV Export ──────────────────────────────────────────────────

@login_required
def export_csv(request):
    """Export filtered expenses as CSV."""
    expenses = Expense.objects.filter(user=request.user).select_related('category')

    # Apply same filters as expense list
    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')

    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    if search:
        expenses = expenses.filter(description__icontains=search)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="expenses_{date.today().isoformat()}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Amount', 'Notes'])

    for expense in expenses:
        writer.writerow([
            expense.date.isoformat(),
            expense.category.name if expense.category else 'Uncategorized',
            expense.description,
            expense.amount,
            expense.notes,
        ])

    return response


# ─── Chart Data API (for AJAX) ───────────────────────────────────

@login_required
def chart_data(request):
    """Return chart data as JSON for dashboard AJAX updates."""
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__month=month,
        date__year=year,
    )

    # Category breakdown
    category_data = (
        monthly_expenses
        .values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Daily spending
    daily_data = (
        monthly_expenses
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    return JsonResponse({
        'category_labels': [
            item['category__name'] or 'Uncategorized'
            for item in category_data
        ],
        'category_amounts': [
            float(item['total']) for item in category_data
        ],
        'category_colors': [
            item['category__color'] or '#8B8B8B'
            for item in category_data
        ],
        'daily_labels': [
            item['day'].strftime('%b %d') for item in daily_data
        ],
        'daily_amounts': [
            float(item['total']) for item in daily_data
        ],
    })
