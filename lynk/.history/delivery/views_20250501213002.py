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
        logger.info(f"Accept request started for {request_id}")
        
        try:
            # Verify delivery person
            if request.user.role != 'delivery':
                logger.warning(f"Non-delivery user {request.user.id} tried to accept request")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Only delivery personnel can accept requests'
                }, status=403)

            # Get the delivery request
            delivery_request = Request.objects.select_related('cart').get(
                id=request_id,
                recipient=request.user,
                status='pending'
            )
            logger.info(f"Found delivery request {delivery_request.id}")

            # Verify cart exists
            if not delivery_request.cart.products.exists():
                logger.warning(f"Empty cart for request {delivery_request.id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Customer cart is empty'
                }, status=400)

            # Calculate total
            total = sum(
                cp.product.price * cp.quantity 
                for cp in delivery_request.cart.products.all()
            ) + delivery_request.delivery_fee
            
            logger.info(f"Creating payment intent for amount {total}")

            # Create Stripe PaymentIntent with timeout
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency='egp',
                metadata={
                    'request_id': delivery_request.id,
                    'user_id': delivery_request.sender.id
                },
                payment_method_types=['card'],
            )
            
            logger.info(f"Created PaymentIntent {payment_intent.id}")

            # Update delivery request
            delivery_request.status = 'accepted'
            delivery_request.stripe_payment_intent_id = payment_intent.id
            delivery_request.save()
            
            logger.info(f"Request {delivery_request.id} accepted successfully")
            
            return JsonResponse({
                'status': 'success',
                'payment_url': f"{payment_intent.next_action.redirect_to_url.url}",
                'message': 'Delivery accepted'
            })

        except Request.DoesNotExist:
            logger.warning(f"Request {request_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Delivery request not found'
            }, status=404)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Payment processing error'
            }, status=500)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
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