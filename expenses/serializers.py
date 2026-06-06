from rest_framework import serializers
from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type']


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    category_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'category', 'category_name', 'category_type',
                  'amount', 'description', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_category_name(self, obj):
        return obj.category.name

    def get_category_type(self, obj):
        return obj.category.category_type
