import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models import functions, aggregates
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import serializers, viewsets

import django_ddf as ddf

from .models import Order, OrderLine, Product

logger = logging.getLogger()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name')


class OrderLineSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderLine
        fields = ('product', 'quantity', 'product_price', 'total_price')
        #exclude = ('order',)


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    order_lines = OrderLineSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'created', 'submitted', 'order_lines')


class OrderOrderingFilter(ddf.OrderingFilter):

    def __init__(self):
        super().__init__(fields={
            # example: model field
            # Order by order creation date
            'created': 'created',

            # example: expression on related model
            # Order by user full name
            'user': functions.Concat(
                models.F('user__first_name'),
                models.Value(' '),
                models.F('user__last_name'),
            ),

            # example: aggregate expression
            'total_quantity': aggregates.Sum(models.F('order_lines__quantity')),
        })


class OrderFilterSet(FilterSet):
    ordering = OrderOrderingFilter()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilterSet

    class Meta:
        model = Order
