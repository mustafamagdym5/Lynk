from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(default='')
    category_image = models.ImageField(null=True, blank=True, upload_to='images/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        def __str__(self):
            return f'Name: { self.name } ,Description: { self.description }'

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(default='')
    item_image = models.ImageField(null=True, blank=True, upload_to='images/')
    category = models.ForeignKey()