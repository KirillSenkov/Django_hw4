from django_filters import rest_framework as filters
from .models import Stock

class StockFilter(filters.FilterSet):
    products = filters.NumberFilter(field_name="products__id", lookup_expr='exact')

    class Meta:
        model = Stock
        fields = ['products']