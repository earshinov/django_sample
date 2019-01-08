from django.contrib.auth.models import User
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False)
    created = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    submitted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id}'


class Product(models.Model):
    name = models.CharField(null=False, blank=False, max_length=256)
    price = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=12)
    
    def __str__(self):
        return self.name


class OrderLine(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, blank=False, related_name='order_lines')
    quantity = models.IntegerField(null=False, blank=False)
    product_price = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=12)
    total_price = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=12)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False, related_name='order_lines')
    
    def __str__(self):
        return f'{self.order}: {self.product.name} x{self.quantity}'
