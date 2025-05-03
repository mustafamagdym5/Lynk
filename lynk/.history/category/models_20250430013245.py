from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=180)
    category_image = models.ImageField(null=True, blank=True, upload_to='images/')