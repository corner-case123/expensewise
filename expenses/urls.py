from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# DRF Router
router = DefaultRouter()
router.register(r'expenses', api_views.ExpenseViewSet, basename='api-expense')
router.register(r'categories', api_views.CategoryViewSet, basename='api-category')

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Authentication
    path('accounts/register/', views.register, name='register'),

    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('expenses/export/', views.export_csv, name='export_csv'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Budget
    path('budget/', views.budget_set, name='budget_set'),

    # Chart data (AJAX)
    path('api/chart-data/', views.chart_data, name='chart_data'),

    # REST API
    path('api/', include(router.urls)),
    path('api/token/', api_views.obtain_token, name='api_token'),
    path('api/summary/', api_views.monthly_summary, name='api_summary'),
]
