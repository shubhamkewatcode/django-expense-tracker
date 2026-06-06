from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    name = models.CharField(max_length=50, unique=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)

    class Meta:
        ordering = ['category_type', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.category.name} - {self.amount}"