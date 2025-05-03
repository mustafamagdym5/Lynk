from django.shortcuts import render, redirect, get_object_or_404

from .models import Request 
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

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
    
from django.http import JsonResponse

class AcceptDeliveryRequest(LoginRequiredMixin, View):
    def post(self, request, request_id):
        delivery_request = get_object_or_404(
            Request, 
            id=request_id, 
            recipient=request.user,
            status='pending'
        )
        
        delivery_request.status = 'accepted'
        delivery_request.save()
        
        # Here you would typically:
        # 1. Notify the customer
        # 2. Update order status
        # 3. Maybe create a DeliveryTask record
        
        return JsonResponse({'status': 'success'})

class RejectDeliveryRequest(LoginRequiredMixin, View):
    def post(self, request, request_id):
        delivery_request = get_object_or_404(
            Request, 
            id=request_id, 
            recipient=request.user,
            status='pending'
        )
        
        delivery_request.status = 'rejected'
        delivery_request.save()
        
        # Notify customer that delivery was rejected
        return JsonResponse({'status': 'success'})