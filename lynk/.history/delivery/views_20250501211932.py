from django.shortcuts import render, redirect, get_object_or_404
from .models import Request 
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import stripe
from django.urls import reverse
from django.conf import settings
from cart.models import Cart, CartProducts

class DeliveryHome(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'delivery':
            return redirect('home')
            
        pending_requests = Request.objects.filter(
            recipient=request.user,
            status='pending'
        ).select_related('sender', 'cart')
        
        return render(request, 'delivery/delivery_home.html', {
            'delivery_requests': pending_requests
        })
    

class AcceptDeliveryRequest(LoginRequiredMixin, View):
    def post(self, request, request_id):
        delivery_request = get_object_or_404(
            Request, 
            id=request_id, 
            recipient=request.user,
            status='pending'
        )
        
        try:
            # Get the customer's cart
            user_cart = Cart.objects.get(user=delivery_request.sender)
            cart_products = CartProducts.objects.filter(cart=user_cart)
            
            if not cart_products.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Customer cart is empty'
                }, status=400)

            # Calculate product total
            product_total = sum(
                cart_product.product.price * cart_product.quantity 
                for cart_product in cart_products
            )
            delivery_fee = delivery_request.delivery_fee
            total = product_total + delivery_fee

            # Prepare line items for Stripe
            line_items = []
            
            # Add products
            for cart_product in cart_products:
                if not cart_product.product.stripe_price_id:
                    cart_product.product.save()  # This should create Stripe price if missing
                    
                line_items.append({
                    'price': cart_product.product.stripe_price_id,
                    'quantity': cart_product.quantity,
                })
            
            # Add delivery fee
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

            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                success_url=(
                    f"{settings.BASE_URL}"
                    f"{reverse('payment:payment_successful')}"
                    f"?session_id={{CHECKOUT_SESSION_ID}}"
                    f"&request_id={delivery_request.id}"
                ),
                cancel_url=(
                    f"{settings.BASE_URL}"
                    f"{reverse('payment:payment_cancelled')}"
                    f"?request_id={delivery_request.id}"
                ),
                metadata={
                    'user_id': delivery_request.sender.id,
                    'cart_id': user_cart.id,
                    'request_id': delivery_request.id,
                    'type': 'combined_payment'
                }
            )

            # Update delivery request
            delivery_request.status = 'accepted'
            delivery_request.stripe_payment_intent_id = checkout_session.payment_intent
            delivery_request.save()

            return JsonResponse({
                'status': 'success',
                'redirect_url': checkout_session.url,
                'message': 'Redirecting to payment'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class RejectDeliveryRequest(LoginRequiredMixin, View):
    def post(self, request, request_id):
        delivery_request = get_object_or_404(
            Request, 
            id=request_id, 
            recipient=request.user,
            status='pending'
        )
        
        try:
            delivery_request.status = 'rejected'
            delivery_request.save()
            
            # Add any additional logic here
            
            return JsonResponse({
                'status': 'success',
                'message': 'Delivery rejected successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    
class ActiveDeliveries(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'delivery':
            return redirect('home')
            
        active_deliveries = Request.objects.filter(
            recipient=request.user,
            status='accepted'
        ).select_related('sender', 'cart')
        
        return render(request, 'delivery/active_deliveries.html', {
            'active_deliveries': active_deliveries
        })

class CheckRequestStatus(LoginRequiredMixin, View):
    def get(self, request, request_id):
        delivery_request = get_object_or_404(
            Request, 
            id=request_id,
            sender=request.user  # Ensure customer can only check their own requests
        )
        
        response_data = {
            'status': delivery_request.status,
            'updated_at': delivery_request.updated_at.isoformat()
        }
        
        # If accepted, include payment URL if available
        if delivery_request.status == 'accepted' and delivery_request.stripe_payment_intent_id:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(
                    delivery_request.stripe_payment_intent_id
                )
                if payment_intent.status == 'requires_payment_method':
                    response_data['payment_url'] = payment_intent.next_action.redirect_to_url.url
            except Exception as e:
                logger.error(f"Error retrieving payment intent: {str(e)}")
        
        return JsonResponse(response_data)