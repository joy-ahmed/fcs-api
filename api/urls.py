# api/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    AccountViewSet, CategoryViewSet, TransactionViewSet,
    BudgetViewSet, GoalViewSet, RegisterViewSet
)

router = DefaultRouter()
router.register('accounts', AccountViewSet, basename='accounts')
router.register('categories', CategoryViewSet, basename='categories')
router.register('transactions', TransactionViewSet, basename='transactions')
router.register('budgets', BudgetViewSet, basename='budgets')
router.register('goals', GoalViewSet, basename='goals')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterViewSet.as_view({'post':'create'}), name='register'),
]

