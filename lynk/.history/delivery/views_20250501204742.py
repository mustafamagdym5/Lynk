from django.shortcuts import render, redirect, get_object_or_404
from .models import Request 
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import stripe

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
            delivery_request.status = 'accepted'
            delivery_request.save()
            
            # Create a payment session with delivery fee
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'egp',
                        'product_data': {
                            'name': 'Delivery Fee',
                        },
                        'unit_amount': int(delivery_request.delivery_fee * 100),
                    },
                    'quantity': 1,
                }],
                success_url=f"{settings.BASE_URL}{reverse('payment:delivery_payment_success')}?request_id={delivery_request.id}",
                cancel_url=f"{settings.BASE_URL}{reverse('payment:delivery_payment_cancelled')}?request_id={delivery_request.id}",
                metadata={
                    'request_id': delivery_request.id,
                    'type': 'delivery_fee'
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'redirect_url': checkout_session.url,
                'message': 'Delivery accepted successfully'
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
            sender=request.user
        )
        return JsonResponse({
            'status': delivery_request.status,
            'updated_at': delivery_request.updated_at.isoformat()
        })