"""
Management command to seed the database with sample data for demo purposes.
Usage: python manage.py seed_data
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from expenses.models import Category, Expense, Budget


class Command(BaseCommand):
    help = 'Seed the database with sample expense data for demo purposes'

    def handle(self, *args, **options):
        # Create demo user if not exists
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'email': 'demo@expensewise.com',
            },
        )
        if created:
            user.set_password('demo1234')
            user.save()
            self.stdout.write(self.style.SUCCESS(
                'Created demo user (username: demo, password: demo1234)'
            ))

        # Create default categories
        Category.create_defaults_for_user(user)
        categories = list(Category.objects.filter(user=user))
        self.stdout.write(f'Categories: {len(categories)}')

        # Sample expense descriptions by category
        expense_samples = {
            'Food & Dining': [
                ('Grocery shopping', 45, 120),
                ('Restaurant dinner', 25, 80),
                ('Coffee shop', 4, 8),
                ('Lunch at work', 10, 18),
                ('Food delivery', 15, 40),
            ],
            'Transportation': [
                ('Gas fill-up', 35, 65),
                ('Uber ride', 8, 25),
                ('Parking fee', 5, 15),
                ('Bus pass', 50, 80),
            ],
            'Housing & Rent': [
                ('Monthly rent', 1200, 1200),
                ('Home repair', 50, 200),
            ],
            'Utilities': [
                ('Electricity bill', 60, 120),
                ('Water bill', 30, 60),
                ('Internet bill', 50, 70),
                ('Phone bill', 40, 60),
            ],
            'Entertainment': [
                ('Movie tickets', 12, 25),
                ('Streaming subscription', 10, 15),
                ('Concert tickets', 40, 100),
                ('Video game', 20, 60),
            ],
            'Healthcare': [
                ('Doctor visit', 30, 100),
                ('Pharmacy', 10, 50),
                ('Gym membership', 30, 50),
            ],
            'Shopping': [
                ('Clothing', 30, 100),
                ('Electronics', 50, 300),
                ('Household items', 15, 50),
            ],
            'Education': [
                ('Online course', 10, 50),
                ('Books', 10, 30),
                ('Stationery', 5, 20),
            ],
            'Travel': [
                ('Hotel booking', 80, 200),
                ('Flight tickets', 150, 400),
            ],
            'Other': [
                ('Miscellaneous', 5, 30),
                ('Gift for friend', 20, 50),
                ('Charity donation', 10, 50),
            ],
        }

        # Generate expenses for the last 3 months
        today = date.today()
        start_date = today.replace(day=1) - timedelta(days=60)
        expense_count = 0

        for day_offset in range(0, (today - start_date).days + 1):
            current_date = start_date + timedelta(days=day_offset)

            # Generate 1-4 expenses per day
            num_expenses = random.randint(1, 4)
            for _ in range(num_expenses):
                category = random.choice(categories)
                samples = expense_samples.get(category.name, [('Expense', 10, 50)])
                description, min_amt, max_amt = random.choice(samples)

                amount = Decimal(str(
                    round(random.uniform(min_amt, max_amt), 2)
                ))

                Expense.objects.create(
                    user=user,
                    category=category,
                    amount=amount,
                    description=description,
                    date=current_date,
                    notes='' if random.random() > 0.3 else 'Sample note',
                )
                expense_count += 1

        # Set budgets for current and previous months
        for month_offset in range(3):
            m = today.month - month_offset
            y = today.year
            if m <= 0:
                m += 12
                y -= 1
            Budget.objects.get_or_create(
                user=user,
                month=m,
                year=y,
                defaults={'amount': Decimal('2000.00')},
            )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {expense_count} sample expenses '
            f'and 3 monthly budgets.'
        ))
        self.stdout.write(self.style.SUCCESS(
            '\nDemo login:\n  Username: demo\n  Password: demo1234'
        ))
