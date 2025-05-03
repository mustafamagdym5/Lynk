from django.core.management.base import BaseCommand
from category.models import Product
import stripe
from django.conf import settings

class Command(BaseCommand):
    help = 'Sync all products with Stripe'

    def handle(self, *args, **options):
        for product in Product.objects.all():
            try:
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully synced: {product.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to sync {product.name}: {str(e)}'))
