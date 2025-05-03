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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    stripe_product_id = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        # Create Stripe product if it doesn't exist
        if not self.stripe_product_id:
            product_data = {
                'name': self.name,
                'description': self.description[:500] if self.description else '',
            }
            
            # Only add image if it exists and has a valid URL
            if self.product_image and hasattr(self.product_image, 'url'):
                try:
                    # Build absolute URL
                    absolute_url = urljoin(settings.BASE_URL, self.product_image.url)
                    product_data['images'] = [absolute_url]
                except:
                    # Skip image if URL is invalid
                    pass
                
            stripe_product = stripe.Product.create(**product_data)
            self.stripe_product_id = stripe_product.id
            
        # Always create a new price when product is saved
        stripe_price = stripe.Price.create(
            product=self.stripe_product_id,
            unit_amount=int(float(self.price) * 100),  # Ensure price is converted properly
            currency='egp',
        )
        self.stripe_price_id = stripe_price.id
            
        super().save(*args, **kwargs)
            
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name