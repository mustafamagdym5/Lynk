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
            if request.user.role != 'delivery':
                logger.warning(f"Non-delivery user {request.user.id} tried to accept request")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Only delivery personnel can accept requests'
                }, status=403)

            delivery_request = Request.objects.select_related('cart').get(
                id=request_id,
                recipient=request.user,
                status='pending'
            )
            logger.info(f"Found delivery request {delivery_request.id}")

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

            # Update delivery request first
            delivery_request.status = 'accepted'
            delivery_request.save()
            
            logger.info(f"Request {delivery_request.id} accepted successfully")
            
            # Return the checkout URL for the customer to pay
            return JsonResponse({
                'status': 'success',
                'checkout_url': reverse('payment:check_out') + f'?delivery_request_id={delivery_request.id}',
                'message': 'Delivery accepted'
            })

        except Request.DoesNotExist:
            logger.warning(f"Request {request_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Delivery request not found'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)


class RejectDeliveryRequest(LoginRequiredMixin, View):
    def post(self, request, request_id):
        try:
            if request.user.role != 'delivery':
                logger.warning(f"Non-delivery user {request.user.id} tried to reject request")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Only delivery personnel can reject requests'
                }, status=403)

            delivery_request = Request.objects.get(
                id=request_id,
                recipient=request.user,
                status='pending'
            )
            
            delivery_request.status = 'rejected'
            delivery_request.save()
            
            logger.info(f"Request {request_id} rejected successfully")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Delivery rejected successfully'
            })
            
        except Request.DoesNotExist:
            logger.warning(f"Request {request_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Delivery request not found'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
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
        try:
            delivery_request = Request.objects.get(
                id=request_id,
                sender=request.user
            )
            
            response_data = {
                'status': delivery_request.status,
                'updated_at': delivery_request.updated_at.isoformat()
            }
            
            return JsonResponse(response_data)
            
        except Request.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Delivery request not found'
            }, status=404)    

class DeliveryAcceptedConfirmation(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'delivery':
            return redirect('home')
        return render(request, 'delivery/delivery_accepted_confirmation.html')
    

class TrackDelivery(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'customer':
            return redirect('home')
            
        # Get the latest delivery request for this customer
        delivery_request = Request.objects.filter(
            sender=request.user,
            status__in=['accepted', 'processing']
        ).order_by('-created_at').first()
        
        if not delivery_request:
            return render(request, 'delivery/no_active_delivery.html')
            
        return render(request, 'delivery/track_delivery.html', {
            'delivery_request': delivery_request,
            'delivery_person': delivery_request.recipient,
            'customer_location': (request.user.latitude, request.user.longitude),
            'delivery_person_location': (delivery_request.recipient.latitude, delivery_request.recipient.longitude)
        })

class UpdateDeliveryLocation(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.role != 'delivery':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
            
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                request.user.latitude = latitude
                request.user.longitude = longitude
                request.user.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class GetDeliveryLocation(LoginRequiredMixin, View):
    def get(self, request, request_id):
        delivery_request = get_object_or_404(Request, id=request_id)
        return JsonResponse({
            'latitude': delivery_request.recipient.latitude,
            'longitude': delivery_request.recipient.longitude
        })