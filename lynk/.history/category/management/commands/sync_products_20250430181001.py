from django.core.management.base import BaseCommand
from category.models import Product

class Command(BaseCommand):
    help = 'Sync all products with Stripe'

    def handle(self, *args, **options):
        for product in Product.objects.all():
            try:
                # Force image URL regeneration
                if product.product_image:
                    product.product_image = product.product_image
                product.save()
                self.stdout.write(f'Synced product: {product.name}')
                if hasattr(product, 'get_absolute_image_url'):
                    self.stdout.write(f'Image URL: {product.get_absolute_image_url()}')
            except Exception as e:
                self.stdout.write(f'Error syncing {product.name}: {str(e)}')