from django.db import connection
from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filters import StockFilter
from rest_framework.filters import SearchFilter
from rest_framework.response import  Response
from rest_framework import status
from logistic.models import Product, Stock, StockProduct
from logistic.serializers import ProductSerializer, StockSerializer


class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'description']

    def create(self, request, *args, **kwargs):
        product_list = request.data.get('products')
        if product_list:
            response = {'products': []}
            for product in product_list:
                serializer = self.get_serializer(data=product)
                if serializer.is_valid():
                    serializer.save()
                    response['products'].append(serializer.data)
                else:
                    response['products'].append({'title': product['title'],
                                                 'errors': serializer.errors
                                                 }
                                                )
            for product in response['products']:
                try:
                    if product['errors']:
                        return Response(response, status=status.HTTP_207_MULTI_STATUS)
                except KeyError:
                    pass
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,
                          status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        Product.objects.all().delete()
        with connection.cursor() as cur:
            cur.execute(
                "ALTER SEQUENCE logistic_product_id_seq RESTART WITH 1;")
        return Response({"message": "All products deleted"},
                        status=status.HTTP_204_NO_CONTENT)


class StockModelViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filterset_class = StockFilter
    filterset_fields = ['products']

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

        #raise ValueError(f'>{StockSerializer(instance).data._dir_}<')
        return Response(StockSerializer(instance).data,
                      status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        Stock.objects.all().delete()
        with connection.cursor() as cur:
            cur.execute(
                "ALTER SEQUENCE logistic_stock_id_seq RESTART WITH 1;")
        return Response({"message": "All stocks deleted"},
                        status=status.HTTP_204_NO_CONTENT)