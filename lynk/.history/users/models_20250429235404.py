from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    role = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

class VendorUser(AbstractUser):
    role = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

class DeliveryUser(AbstractUser):
    role = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    cost_per_km = models.DecimalField(max_digits=5, decimal_places=1)