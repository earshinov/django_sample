from django.contrib import admin

from .models import Order, OrderLine, Product

admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(Product)
