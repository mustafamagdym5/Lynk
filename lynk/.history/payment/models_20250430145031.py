from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class UserPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_checkout_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    product_name = models.CharField(max_length=500, blank=True)