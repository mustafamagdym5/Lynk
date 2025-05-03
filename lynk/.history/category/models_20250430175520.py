from django.db import models
from django.utils.text import slugify
from django.conf import settings
import stripe

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
    stripe_price_id = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        # Create/update Stripe product
        if not self.stripe_price_id:  # If new product
            stripe_product = stripe.Product.create(
                name=self.name,
                description=self.description,
                images=[self.product_image.url] if self.product_image else None,
            )
            
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(self.price * 100),  # Convert to cents
                currency='egp',
            )
            
            self.stripe_price_id = stripe_price.id
        else:
            # Update existing product if needed
            pass
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name