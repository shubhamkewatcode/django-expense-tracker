from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# DRF Router for ViewSets
router = DefaultRouter()
router.register('transactions', views.TransactionViewSet, basename='api-transaction')
router.register('categories', views.CategoryViewSet, basename='api-category')

urlpatterns = [
    # ============ Web Views ============
    path('signup/', views.signup_view, name='signup'),
    path('', views.dashboard_view, name='dashboard'),

    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction-edit'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction-delete'),

    # ============ REST API ============
    path('api/', include(router.urls)),
    path('api/auth/token/', obtain_auth_token, name='api-token'),

    # Custom Analytics Endpoints
    path('api/analytics/category-totals/', views.CategoryTotalsAPI.as_view(), name='api-category-totals'),
    path('api/analytics/monthly-summary/', views.MonthlySummaryAPI.as_view(), name='api-monthly-summary'),
]
