from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Expense, Budget


class ModelTests(TestCase):
    """Tests for the data models."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
        )

    def test_category_creation(self):
        category = Category.objects.create(
            user=self.user,
            name='Food',
            color='#FF6384',
        )
        self.assertEqual(str(category), 'Food')
        self.assertEqual(category.user, self.user)

    def test_category_defaults_created(self):
        Category.create_defaults_for_user(self.user)
        count = Category.objects.filter(user=self.user).count()
        self.assertEqual(count, 10)

    def test_expense_creation(self):
        category = Category.objects.create(
            user=self.user, name='Food', color='#FF6384',
        )
        expense = Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('25.50'),
            description='Lunch',
            date=date.today(),
        )
        self.assertEqual(expense.amount, Decimal('25.50'))
        self.assertIn('Lunch', str(expense))

    def test_budget_creation(self):
        budget = Budget.objects.create(
            user=self.user,
            month=11,
            year=2024,
            amount=Decimal('1000.00'),
        )
        self.assertEqual(budget.amount, Decimal('1000.00'))
        self.assertIn('1000', str(budget))


class ViewTests(TestCase):
    """Tests for the web views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
        )
        Category.create_defaults_for_user(self.user)
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_dashboard_redirect_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_expense_list(self):
        response = self.client.get(reverse('expense_list'))
        self.assertEqual(response.status_code, 200)

    def test_expense_create(self):
        category = Category.objects.filter(user=self.user).first()
        response = self.client.post(reverse('expense_create'), {
            'category': category.pk,
            'amount': '50.00',
            'description': 'Test expense',
            'date': date.today().isoformat(),
            'notes': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Expense.objects.filter(description='Test expense').exists()
        )

    def test_expense_edit(self):
        category = Category.objects.filter(user=self.user).first()
        expense = Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('25.00'),
            description='Original',
            date=date.today(),
        )
        response = self.client.post(
            reverse('expense_edit', kwargs={'pk': expense.pk}),
            {
                'category': category.pk,
                'amount': '30.00',
                'description': 'Updated',
                'date': date.today().isoformat(),
                'notes': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        expense.refresh_from_db()
        self.assertEqual(expense.description, 'Updated')
        self.assertEqual(expense.amount, Decimal('30.00'))

    def test_expense_delete(self):
        category = Category.objects.filter(user=self.user).first()
        expense = Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('25.00'),
            description='To delete',
            date=date.today(),
        )
        response = self.client.post(
            reverse('expense_delete', kwargs={'pk': expense.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_register_new_user(self):
        self.client.logout()
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Check default categories were created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(
            Category.objects.filter(user=new_user).count(), 10
        )

    def test_csv_export(self):
        category = Category.objects.filter(user=self.user).first()
        Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('50.00'),
            description='CSV test',
            date=date.today(),
        )
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('CSV test', response.content.decode())

    def test_budget_set(self):
        today = date.today()
        response = self.client.post(reverse('budget_set'), {
            'month': today.month,
            'year': today.year,
            'amount': '1500.00',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Budget.objects.filter(
                user=self.user, month=today.month, year=today.year,
            ).exists()
        )

    def test_category_list(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)

    def test_expense_filter_by_category(self):
        category = Category.objects.filter(user=self.user).first()
        Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('20.00'),
            description='Filtered',
            date=date.today(),
        )
        response = self.client.get(
            reverse('expense_list'), {'category': category.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtered')

    def test_expense_search(self):
        category = Category.objects.filter(user=self.user).first()
        Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('15.00'),
            description='UniqueSearchTerm',
            date=date.today(),
        )
        response = self.client.get(
            reverse('expense_list'), {'search': 'UniqueSearchTerm'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'UniqueSearchTerm')

    def test_other_user_cannot_see_expenses(self):
        """Ensure users can only see their own expenses."""
        other_user = User.objects.create_user(
            username='other', password='pass123',
        )
        category = Category.objects.create(
            user=other_user, name='Private', color='#000',
        )
        Expense.objects.create(
            user=other_user,
            category=category,
            amount=Decimal('100.00'),
            description='Secret expense',
            date=date.today(),
        )
        response = self.client.get(reverse('expense_list'))
        self.assertNotContains(response, 'Secret expense')


class APITests(TestCase):
    """Tests for the REST API."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',
            email='api@example.com',
        )
        Category.create_defaults_for_user(self.user)
        self.client.force_authenticate(user=self.user)

    def test_list_expenses(self):
        response = self.client.get('/api/expenses/')
        self.assertEqual(response.status_code, 200)

    def test_create_expense(self):
        category = Category.objects.filter(user=self.user).first()
        response = self.client.post('/api/expenses/', {
            'category': category.pk,
            'amount': '35.00',
            'description': 'API test expense',
            'date': date.today().isoformat(),
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], 'API test expense')

    def test_update_expense(self):
        category = Category.objects.filter(user=self.user).first()
        expense = Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('25.00'),
            description='Original API',
            date=date.today(),
        )
        response = self.client.patch(f'/api/expenses/{expense.pk}/', {
            'description': 'Updated API',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'Updated API')

    def test_delete_expense(self):
        category = Category.objects.filter(user=self.user).first()
        expense = Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('25.00'),
            description='Delete me API',
            date=date.today(),
        )
        response = self.client.delete(f'/api/expenses/{expense.pk}/')
        self.assertEqual(response.status_code, 204)

    def test_list_categories(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)

    def test_monthly_summary(self):
        category = Category.objects.filter(user=self.user).first()
        Expense.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('50.00'),
            description='Summary test',
            date=date.today(),
        )
        response = self.client.get('/api/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data['total_spent']), 50.00)

    def test_token_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/token/', {
            'username': 'apiuser',
            'password': 'apipass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/expenses/')
        self.assertEqual(response.status_code, 401)
