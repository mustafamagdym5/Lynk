# management/commands/sync_products.py
from django.core.management.base import BaseCommand
from category.models import Product

class Command(BaseCommand):
    help = 'Sync all products with Stripe'

    def handle(self, *args, **options):
        for product in Product.objects.all():
            product.save()
            self.stdout.write(f'Synced product: {product.name}')