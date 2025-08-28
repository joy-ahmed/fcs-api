from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=120)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='BDT')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user})"

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ["-created_at"]

class Category(models.Model):
    TYPE_CHOICES = (("income", "Income"), ("expense", "Expense"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    

class Transaction(models.Model):
    TYPE_CHOICES = (("income", "Income"), ("expense", "Expense"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    notes = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type.capitalize()}: {self.amount} ({self.user})"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_at"]


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField(help_text="Budget month (use first day of the month)")

    def __str__(self):
        return f"{self.name} ({self.month.strftime('%Y %m')})"
    


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=120)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    current_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    target_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def progress_pct(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0

    def __str__(self):
        return f"{self.name} ({self.user})"
