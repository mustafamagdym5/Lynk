from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    category_image = models.ImageField(null=True, blank=True, upload_to='images/')