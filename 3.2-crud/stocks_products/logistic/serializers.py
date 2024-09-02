from rest_framework import serializers
from .models import Product, Stock, StockProduct

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['id', 'product', 'quantity', 'price']



class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        # Извлекаем позиции из валидированных данных
        positions_data = validated_data.pop('positions', [])

        # Создаем объект Stock
        stock = Stock.objects.create(**validated_data)

        # Создаем связанные объекты StockProduct
        for position_data in positions_data:
            StockProduct.objects.create(stock=stock, **position_data)

        return stock
