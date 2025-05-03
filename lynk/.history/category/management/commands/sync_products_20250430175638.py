from django.core.management.base import BaseCommand
from category.models import Product
import stripe
from django.conf import settings

class Command(BaseCommand):
    help = 'Sync products with Stripe'

    def handle(self, *args, **options):
        for product in Product.objects.all():
            product.save() 