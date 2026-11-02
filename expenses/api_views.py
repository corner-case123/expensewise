from decimal import Decimal

from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import Expense, Category, Budget
from .serializers import (
    ExpenseSerializer, CategorySerializer, MonthlySummarySerializer,
)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for expenses.
    Supports list, create, retrieve, update, and delete.
    Filterable by category, date range. Searchable by description.
    """
    serializer_class = ExpenseSerializer
    filterset_fields = ['category', 'date']
    search_fields = ['description', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        queryset = Expense.objects.filter(
            user=self.request.user
        ).select_related('category')

        # Custom date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for categories."""
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(
            user=self.request.user
        ).annotate(expense_count=Count('expenses'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    """Get or create an auth token for API access."""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
        })

    return Response(
        {'error': 'Invalid credentials.'},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_summary(request):
    """Return monthly spending summary."""
    today = timezone.now().date()
    month = int(request.query_params.get('month', today.month))
    year = int(request.query_params.get('year', today.year))

    expenses = Expense.objects.filter(
        user=request.user,
        date__month=month,
        date__year=year,
    )

    total_spent = expenses.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    category_breakdown = list(
        expenses
        .values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    budget = Budget.objects.filter(
        user=request.user, month=month, year=year
    ).first()

    data = {
        'month': month,
        'year': year,
        'total_spent': total_spent,
        'expense_count': expenses.count(),
        'budget_amount': budget.amount if budget else None,
        'category_breakdown': [
            {
                'category': item['category__name'] or 'Uncategorized',
                'total': float(item['total']),
                'count': item['count'],
            }
            for item in category_breakdown
        ],
    }

    return Response(data)
