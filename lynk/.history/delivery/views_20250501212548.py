from django.shortcuts import render, redirect, get_object_or_404
from .models import Request 
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import stripe
from django.urls import reverse
from django.conf import settings
from cart.models import Cart, CartProducts
import logging

logger = logging.getLogger(__name__)

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
        logger.info(f"Accept request received for ID: {request_id}")
        logger.info(f"Request user: {request.user}, role: {request.user.role}")
        delivery_request = get_object_or_404(
            Request, 
            id=request_id, 
            recipient=request.user,
            status='pending'
        )
        
        try:
            # Get customer's cart
            user_cart = delivery_request.cart
            cart_products = user_cart.products.all()
            
            if not cart_products.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Customer cart is empty'
                }, status=400)

            # Calculate totals
            product_total = sum(
                cp.product.price * cp.quantity 
                for cp in cart_products
            )
            total_amount = int((product_total + delivery_request.delivery_fee) * 100)
            
            # Create PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency='egp',
                customer=delivery_request.sender.stripe_customer_id,
                metadata={
                    'request_id': delivery_request.id,
                    'user_id': delivery_request.sender.id,
                    'cart_id': user_cart.id
                },
                description=f"Payment for order with delivery (Request #{delivery_request.id})",
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            # Update delivery request
            delivery_request.status = 'accepted'
            delivery_request.stripe_payment_intent_id = payment_intent.id
            delivery_request.save()
            
            return JsonResponse({
                'status': 'success',
                'payment_url': payment_intent.next_action.redirect_to_url.url,
                'message': 'Delivery accepted'
            })
            
        except Exception as e:
            logger.error(f"Error accepting delivery: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Could not process acceptance'
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
            sender=request.user
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