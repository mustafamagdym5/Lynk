from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import stripe
from django.conf import settings
from cart.models import Cart, CartProducts
from .models import UserPayment

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
        user_cart = Cart.objects.get(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)

        if not request.user.is_authenticated:
            return redirect(f'{settings.BASE_URL}{reverse("account_login")}?next={request.get_full_path()}')
        
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
            success_url = f'{settings.BASE_URL}{reverse("payment_successful")}?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url = f'{settings.BASE_URL}{reverse("payment_cancelled")}',
        )
        return redirect(checkout_session.url, code=303)  


class PaymentSuccessful(View):
    def get(self, request):
        checkout_session_id = request.GET.get('session_id', None)
    
        if checkout_session_id:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            customer_id = session.customer
            customer = stripe.Customer.retrieve(customer_id)
            
            line_item = stripe.checkout.Session.list_line_items(checkout_session_id).data[0]
            UserPayment.objects.get_or_create(
                user = request.user, 
                stripe_customer_id = customer_id,
                stripe_checkout_id = checkout_session_id,
                stripe_product_id = line_item.price.product,
                product_name = line_item.description,
                quantity = line_item.quantity,
                price = line_item.price.unit_amount / 100.0,
                currency = line_item.price.currency,
                has_paid = True
            )
        
        return render(request, 'a_stripe/payment_successful.html', {'customer': customer})

    

class PaymentCancelled(View):
    def get(self, request):
        return render(request, 'payment/payment_cancelled.html')