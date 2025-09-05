from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Account, Category, Transaction, Budget, Goal
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer,
    BudgetSerializer, GoalSerializer, RegisterSerializer, User
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
        })
    

@api_view(["GET"])
@permission_classes([AllowAny])
def check_user_exists(request):
    """
    Check if a username or email already exists.
    Usage: /auth/check-user/?username=foo&email=bar@example.com
    """
    username = request.GET.get("username")
    email = request.GET.get("email")
    exists = False

    if username and User.objects.filter(username=username).exists():
        exists = True
    if email and User.objects.filter(email=email).exists():
        exists = True

    return Response({"exists": exists})

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['type', 'category__id', 'date']
    search_fields = ['notes']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        # ✅ Save the transaction
        serializer.save(user=self.request.user)

        # ✅ Access the saved instance
        transaction = serializer.instance  
        account = transaction.account

        if transaction.type == "income":
            account.balance = str(float(account.balance) + float(transaction.amount))
        elif transaction.type == "expense":
            account.balance = str(float(account.balance) - float(transaction.amount))

        account.save()

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        # return simple month status for current month
        from django.utils import timezone
        now = timezone.now()
        month_start = now.replace(day=1).date()
        budgets = self.get_queryset().filter(month__year=month_start.year, month__month=month_start.month)
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)