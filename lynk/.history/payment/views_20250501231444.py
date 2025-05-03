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
from decimal import Decimal


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
        
        # Get delivery fee if request exists
        delivery_fee = Decimal('0.00')
        delivery_request_id = request.GET.get('delivery_request_id')
        if delivery_request_id:
            try:
                delivery_request = Request.objects.get(
                    id=delivery_request_id,
                    sender=request.user,
                    status='accepted'
                )
                delivery_fee = delivery_request.delivery_fee
            except Request.DoesNotExist:
                pass

        product_cost = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)
        total = product_cost + delivery_fee

        ctx = {
            'cart_items': cart_products,
            'product_total': product_cost,
            'delivery_fee': delivery_fee,
            'total': total,
            'delivery_request_id': delivery_request_id,
        }
        return render(request, 'payment/check_out.html', ctx)
    
    def post(self, request):
        user_cart = Cart.objects.get(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        
        if not cart_products.exists():
            return redirect('cart:view_cart')
        
        # Get delivery fee if request exists
        delivery_fee = Decimal('0.00')
        delivery_request_id = request.POST.get('delivery_request_id')
        if delivery_request_id:
            try:
                delivery_request = Request.objects.get(
                    id=delivery_request_id,
                    sender=request.user,
                    status='accepted'
                )
                delivery_fee = delivery_request.delivery_fee
            except Request.DoesNotExist:
                pass

        line_items = []
        # Add products
        for cart_product in cart_products:
            if not cart_product.product.stripe_price_id:
                cart_product.product.save()
                
            line_items.append({
                'price': cart_product.product.stripe_price_id,
                'quantity': cart_product.quantity,
            })
        
        # Add delivery fee if applicable
        if delivery_fee > 0:
            # Create delivery fee product
            delivery_product = stripe.Product.create(name="Delivery Fee")
            delivery_price = stripe.Price.create(
                product=delivery_product.id,
                unit_amount=int(delivery_fee * 100),
                currency='egp'
            )
            
            line_items.append({
                'price': delivery_price.id,
                'quantity': 1,
            })

        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            payment_method_types=['card'],
            mode='payment',
            success_url=f'{settings.BASE_URL}{reverse("payment:payment_successful")}?session_id={{CHECKOUT_SESSION_ID}}&delivery_request_id={delivery_request_id or ""}',
            cancel_url=f'{settings.BASE_URL}{reverse("payment:payment_cancelled")}',
            metadata={
                'user_id': request.user.id,
                'cart_id': user_cart.id,
                'delivery_request_id': delivery_request_id or ''
            },
        )
        
        # Save payment intent to delivery request if applicable
        if delivery_request_id:
            Request.objects.filter(id=delivery_request_id).update(
                stripe_payment_intent_id=checkout_session.payment_intent
            )
        
        return redirect(checkout_session.url, code=303)

logger = logging.getLogger(__name__)

class PaymentSuccessful(View):
    def get(self, request):
        checkout_session_id = request.GET.get('session_id')
        delivery_request_id = request.GET.get('delivery_request_id')
        
        if not checkout_session_id:
            return render(request, 'payment/payment_successful.html')
            
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            
            # Handle the payment record
            try:
                line_item = stripe.checkout.Session.list_line_items(checkout_session_id).data[0]
                UserPayment.objects.get_or_create(
                    user=request.user,
                    stripe_checkout_id=checkout_session_id,
                    stripe_product_id=line_item.price.product,
                    product_name=line_item.description,
                    quantity=line_item.quantity,
                    price=line_item.price.unit_amount / 100.0,
                    currency=line_item.price.currency,
                    has_paid=True
                )
            except Exception as e:
                logger.error(f"Error creating payment record: {str(e)}")

            # Handle delivery request updates
            if delivery_request_id:
                try:
                    Request.objects.filter(
                        id=delivery_request_id,
                        sender=request.user
                    ).update(
                        payment_status='completed',
                        stripe_payment_intent=session.payment_intent,
                        status='processing'
                    )
                except Exception as e:
                    logger.error(f"Error updating delivery request: {str(e)}")

            # Clear the user's cart
            try:
                user_cart = Cart.objects.get(user=request.user)
                user_cart.products.all().delete()
            except Cart.DoesNotExist:
                pass

            return render(request, 'payment/payment_successful.html', {
                'customer': session.get('customer_details', {}),
                'payment_intent': session.payment_intent
            })

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error in payment success: {str(e)}")
            return render(request, 'payment/payment_successful.html')
        except Exception as e:
            logger.error(f"Unexpected error in payment success: {str(e)}")
            return render(request, 'payment/payment_successful.html')

class PaymentCancelled(View):
    def get(self, request):
        request_id = request.GET.get('request_id')
        if request_id:
            try:
                # Reset the delivery request if payment was cancelled
                Request.objects.filter(id=request_id).update(
                    status='accepted',  # Keep as accepted but not paid
                    payment_status='pending'
                )
            except Request.DoesNotExist:
                pass
                
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