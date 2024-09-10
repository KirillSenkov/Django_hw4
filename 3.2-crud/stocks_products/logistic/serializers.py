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
        positions_data = validated_data.pop('positions', [])

        stock = Stock.objects.create(**validated_data)

        for position_data in positions_data:
            StockProduct.objects.create(stock=stock, **position_data)

        return stock

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        positions_data = request.data.pop('positions', [])

        existing_positions = {position.product_id: position for position in instance.positions.all()}

        for position_data in positions_data:
            product_id = position_data['product']
            if product_id in existing_positions:
                position = existing_positions[product_id]
                position.quantity = position_data.get('quantity', position.quantity)
                position.price = position_data.get('price', position.price)
                position.save()
            else:
                StockProduct.objects.create(stock=instance, **position_data)

        return Response(StockSerializer(instance).data,
                      status=status.HTTP_200_OK)