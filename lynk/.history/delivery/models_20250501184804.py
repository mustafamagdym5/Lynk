from django.db import models
from django.conf import settings

# Create your models here.
class Request(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE
    )

    is_delivery_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.sender.username} to {self.recipient.username}"
