from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from .models import Transaction, Category
from .forms import SignupForm, TransactionForm


from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.db.models.functions import TruncMonth
from .serializers import CategorySerializer, TransactionSerializer


# ====================== AUTHENTICATION ======================

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


# ====================== DASHBOARD ======================

@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    current_month_start = today.replace(day=1)

    # All transactions for current month
    monthly_txns = Transaction.objects.filter(
        user=user,
        date__gte=current_month_start,
        date__lte=today
    )

    # Calculate totals
    income_total = monthly_txns.filter(
        category__category_type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    expense_total = monthly_txns.filter(
        category__category_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = income_total - expense_total

    # Recent 5 transactions
    recent_txns = Transaction.objects.filter(user=user)[:5]

    context = {
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'recent_txns': recent_txns,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'expenses/dashboard.html', context)


# ====================== TRANSACTION CRUD (CBV) ======================

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'expenses/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'expenses/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Transaction'
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'expenses/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Transaction'
        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'expenses/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Each user only sees their own transactions
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign the logged-in user when creating
        serializer.save(user=self.request.user)

class CategoryTotalsAPI(APIView):
    """
    Returns expense totals grouped by category for the current month.
    Used by the pie chart on the dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        current_month_start = today.replace(day=1)

        # Get all expense transactions for the current month, grouped by category
        data = (
            Transaction.objects
            .filter(
                user=request.user,
                category__category_type='expense',
                date__gte=current_month_start,
                date__lte=today
            )
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        labels = [item['category__name'] for item in data]
        values = [float(item['total']) for item in data]

        return Response({
            'labels': labels,
            'values': values
        })


class MonthlySummaryAPI(APIView):
    """
    Returns income and expense totals for the last 6 months.
    Used by the bar chart on the dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)

        # Group by month and category type
        data = (
            Transaction.objects
            .filter(user=request.user, date__gte=six_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month', 'category__category_type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Restructure data into a chart-friendly format
        result = {}
        for item in data:
            month_label = item['month'].strftime('%b %Y')
            if month_label not in result:
                result[month_label] = {'income': 0, 'expense': 0}
            result[month_label][item['category__category_type']] = float(item['total'])

        return Response({
            'labels': list(result.keys()),
            'income': [result[m]['income'] for m in result],
            'expense': [result[m]['expense'] for m in result],
        })
