from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import stripe
from django.conf import settings
from cart.models import Cart, CartProducts

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class HomePayment(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'payment/payment_home.html', {})
    
class ProductView(LoginRequiredMixin, View):
    def get(self, request):
        product_id = 'prod_SCFzvX7BeEfYn5'
        product = stripe.Product.retrieve(product_id)
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        cost = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)

        ctx = {
            'product': product,
            'cart_items': cart_products,
            'total': cost,
        }

        return render(request, 'payment/check_out.html', ctx)