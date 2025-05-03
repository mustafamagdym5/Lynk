from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import stripe
from django.conf import settings
from cart.models import Cart, CartProducts
from .models import UserPayment
from django.core import management
import logging
from delivery.models import Request


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class HomePayment(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'payment/payment_home.html', {})
    
class CheckOutView(LoginRequiredMixin, View):
    def get(self, request):
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        
        if not cart_products.exists():
            return redirect('cart:view_cart')
        
        cost = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)

        ctx = {
            'cart_items': cart_products,
            'total': cost,
        }
        return render(request, 'payment/check_out.html', ctx)
    
    def post(self, request):
        user_cart = Cart.objects.get(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        
        if not cart_products.exists():
            return redirect('cart:view_cart')
        
        line_items = []
        for cart_product in cart_products:
            # Ensure product has Stripe data
            if not cart_product.product.stripe_price_id:
                cart_product.product.save()
                
            line_items.append({
                'price': cart_product.product.stripe_price_id,
                'quantity': cart_product.quantity,
                'adjustable_quantity': {
                    'enabled': True,
                    'minimum': 1,
                    'maximum': 10,
                },
            })

        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            payment_method_types=['card'],
            mode='payment',
            customer_creation='always',
            success_url=f'{settings.BASE_URL}{reverse("payment:payment_successful")}?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.BASE_URL}{reverse("payment:payment_cancelled")}',
            metadata={
                'user_id': request.user.id,
                'cart_id': user_cart.id,
            },
            allow_promotion_codes=True,
        )
        return redirect(checkout_session.url, code=303)


logger = logging.getLogger(__name__)

class PaymentSuccessful(View):
    def get(self, request):
        checkout_session_id = request.GET.get('session_id', None)
    
        if checkout_session_id:
            try:
                session = stripe.checkout.Session.retrieve(checkout_session_id)
                customer_id = session.customer
                customer = stripe.Customer.retrieve(customer_id)
                
                line_item = stripe.checkout.Session.list_line_items(checkout_session_id).data[0]
                UserPayment.objects.get_or_create(
                    user=request.user, 
                    stripe_customer_id=customer_id,
                    stripe_checkout_id=checkout_session_id,
                    stripe_product_id=line_item.price.product,
                    product_name=line_item.description,
                    quantity=line_item.quantity,
                    price=line_item.price.unit_amount / 100.0,
                    currency=line_item.price.currency,
                    has_paid=True
                )
                
                # Clear the user's cart after successful payment
                try:
                    user_cart = Cart.objects.get(user=request.user)
                    cart_items_count = user_cart.products.count()
                    user_cart.products.all().delete()  # Clear all cart items
                    logger.info(f"Cleared {cart_items_count} items from cart for user {request.user.username}")
                except Cart.DoesNotExist:
                    logger.warning(f"No cart found for user {request.user.username}")
                
            except Exception as e:
                logger.error(f"Error processing payment success: {str(e)}")
                # You might want to redirect to an error page here
        
        return render(request, 'payment/payment_successful.html', {'customer': customer})

class PaymentCancelled(View):
    def get(self, request):
        return render(request, 'payment/payment_cancelled.html')
    

class DeliveryPaymentSuccessful(View):
    def get(self, request):
        request_id = request.GET.get('request_id')
        if not request_id:
            return redirect('payment:payment_cancelled')
        
        try:
            delivery_request = Request.objects.get(id=request_id)
            delivery_request.payment_status = 'completed'
            delivery_request.save()
            
            # Now redirect to product payment
            return redirect('payment:check_out')
            
        except Request.DoesNotExist:
            return redirect('payment:payment_cancelled')

class DeliveryPaymentCancelled(View):
    def get(self, request):
        request_id = request.GET.get('request_id')
        if request_id:
            try:
                delivery_request = Request.objects.get(id=request_id)
                delivery_request.status = 'pending'
                delivery_request.payment_status = 'pending'
                delivery_request.save()
            except Request.DoesNotExist:
                pass
                
        return render(request, 'payment/payment_cancelled.html')