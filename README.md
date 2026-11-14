# ExpenseWise — Personal Expense Tracker & Budget Manager

A full-stack Django web application for tracking personal expenses, setting monthly budgets, and visualizing spending patterns with interactive charts.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![DRF](https://img.shields.io/badge/DRF-3.15-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

## Features

- **User Authentication** — Register, login, logout with Django's built-in auth
- **Interactive Dashboard** — Monthly spending summary with Chart.js pie & line charts
- **Expense Management** — Full CRUD with categories, dates, amounts, and notes
- **Custom Categories** — Create personalized expense categories with colors
- **Budget Tracking** — Set monthly budgets with visual progress indicators
- **Smart Filtering** — Filter expenses by date range, category, or search keywords
- **CSV Export** — Download filtered expense data as CSV
- **REST API** — Full CRUD API with token authentication using Django REST Framework
- **Responsive Design** — Mobile-friendly Bootstrap 5 interface

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12, Django 5.1 |
| REST API | Django REST Framework 3.15 |
| Database | SQLite (dev) / PostgreSQL (prod-ready) |
| Frontend | Django Templates, Bootstrap 5.3, Chart.js 4 |
| Authentication | Django built-in auth + DRF Token Auth |

## Quick Start

### Prerequisites
- Python 3.10+ (or Miniconda/Anaconda)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/expensewise.git
cd expensewise

# Create virtual environment (or use conda)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data.json

# Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Get auth token |
| GET | `/api/expenses/` | List expenses |
| POST | `/api/expenses/` | Create expense |
| GET | `/api/expenses/{id}/` | Get expense detail |
| PUT | `/api/expenses/{id}/` | Update expense |
| DELETE | `/api/expenses/{id}/` | Delete expense |
| GET | `/api/categories/` | List categories |
| GET | `/api/summary/` | Monthly summary |

### API Authentication

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -d "username=your_user&password=your_pass"

# Use token
curl -H "Authorization: Token YOUR_TOKEN" \
  http://127.0.0.1:8000/api/expenses/
```

## Project Structure

```
expensewise/
├── manage.py
├── requirements.txt
├── config/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── expenses/            # Main application
│   ├── models.py        # Data models
│   ├── views.py         # Template views
│   ├── api_views.py     # REST API views
│   ├── serializers.py   # DRF serializers
│   ├── forms.py         # Django forms
│   ├── urls.py          # URL routing
│   ├── admin.py         # Admin config
│   └── tests.py         # Test suite
├── templates/           # HTML templates
└── static/              # CSS, JS assets
```

## Screenshots

### Dashboard
The dashboard shows monthly spending overview with interactive pie and line charts.

### Expense List
Filterable, searchable expense list with pagination and CSV export.

## Running Tests

```bash
python manage.py test expenses -v 2
```

## License

MIT License — feel free to use this project as a portfolio piece or learning reference.
