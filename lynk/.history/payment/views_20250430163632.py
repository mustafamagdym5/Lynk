from django.shortcuts import render,redirect
from django.urls import reverse
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
        prices = stripe.Price.list(product=product_id)
        price = prices.data[0]
        product_price = price.unit_amount / 100
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        cost = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)

        ctx = {
            'product': product,
            'cart_items': cart_products,
            'total': cost,
            'product_price': product_price,
        }

        return render(request, 'payment/check_out.html', ctx)
    
    def post(self, request):
        price_id = request.POST.get('price_id')
        quantity = int(request.POST.get('quantity'))
        checkout_session = stripe.checkout.Session.create(
            line_items = [
                {
                    'price': price_id,
                    'quantity': quantity,
                },
            ],
            payment_method_types = ['card'],
            mode = 'payment',
            customer_creation = 'always',
            success_url = f'{settings.BASE_URL}{reverse("payment:payment_successful")}?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url = f'{settings.BASE_URL}{reverse("payment:payment_cancelled")}',
        )
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        cart_products
        return redirect(checkout_session.url, code=303)  


class PaymentSuccessful(View):
    def get(self, request):
        return render(request, 'payment/payment_successful.html')
    

class PaymentCancelled(View):
    def get(self, request):
        return render(request, 'payment/payment_cancelled.html')