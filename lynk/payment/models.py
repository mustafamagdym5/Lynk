from django.db import models
from django.contrib.auth import get_user_model
from category.models import Product

User = get_user_model()


class StripeProduct(models.Model):
    item = models.OneToOneField(Product, on_delete=models.CASCADE)
    stripe_product_id = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.item.name} - {self.stripe_product_id}"


class UserPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_checkout_id = models.CharField(max_length=255, blank=True)
    stripe_product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=500, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    currency = models.CharField(max_length=3, blank=True, default='EGP')
    has_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.product_name} - Paid: {self.has_paid}"