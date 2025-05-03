from django.db import models
from django.conf import settings
from cart.models import Cart

class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_requests', 
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='received_requests', 
        on_delete=models.CASCADE
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='delivery_requests'
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    distance = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed')],
        default='pending'
    )
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    payment_required = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f"Request #{self.id} from {self.sender} to {self.recipient} - {self.status}"