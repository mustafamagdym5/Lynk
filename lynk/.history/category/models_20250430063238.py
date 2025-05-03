from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(default='Explore our wide selection of products in this category')
    category_image = models.ImageField(null=True, blank=True, upload_to='images/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        def __str__(self):
            return self.name


class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(default='')
    product_image = models.ImageField(null=True, blank=True, upload_to='images/')
    price = models.DecimalField(max_digits=9, decimal_places=1, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        def __str__(self):
            return self.name