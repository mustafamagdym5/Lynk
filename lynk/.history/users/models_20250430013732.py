from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class CustomUser(AbstractUser):
    role = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField()

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

class VendorUser(AbstractUser):
    role = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

    groups = models.ManyToManyField(
        Group,
        related_name="vendoruser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="vendoruser_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

class DeliveryUser(AbstractUser):
    role = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    cost_per_km = models.DecimalField(max_digits=5, decimal_places=1)

    groups = models.ManyToManyField(
        Group,
        related_name="deliveryuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="deliveryuser_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )