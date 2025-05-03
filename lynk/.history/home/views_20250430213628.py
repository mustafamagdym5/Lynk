from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from geopy.distance import geodesic
import math
from decimal import Decimal
import json
from .models import DeliveryRequest

class SelectDelivery(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.latitude or not request.user.longitude:
            return redirect('location:choose_location')
        
        user_location = (request.user.latitude, request.user.longitude)
        deliveries = CustomUser.objects.filter(role='delivery')
        
        delivery_list = []
        for delivery in deliveries:
            if delivery.latitude and delivery.longitude:
                delivery_location = (delivery.latitude, delivery.longitude)
                distance_km = geodesic(user_location, delivery_location).km
                
                estimated_time_min = math.ceil((distance_km / 30) * 60)
                cost = (Decimal(str(distance_km)) * delivery.cost_per_km).quantize(Decimal('0.00'))
                
                delivery_list.append({
                    'delivery': delivery,
                    'distance_km': round(distance_km, 1),
                    'estimated_time_min': estimated_time_min,
                    'cost': cost
                })
        
        delivery_list.sort(key=lambda x: x['distance_km'])
        
        ctx = {
            'delivery_list': delivery_list,
            'user_location': user_location
        }
        return render(request, 'customer/select_delivery.html', ctx)

@method_decorator(csrf_exempt, name='dispatch')
class DeliveryResponseView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        try:
            data = json.loads(request.body)
            delivery_request = DeliveryRequest.objects.get(
                id=request_id,
                delivery_person=request.user
            )
            
            if data.get('action') == 'accept':
                delivery_request.status = 'accepted'
                delivery_request.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Delivery accepted successfully'
                })
            elif data.get('action') == 'reject':
                delivery_request.status = 'rejected'
                delivery_request.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Delivery rejected'
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

class CreateDeliveryRequestView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            delivery_person = CustomUser.objects.get(
                id=data.get('delivery_person_id'),
                role='delivery'
            )
            
            delivery_request = DeliveryRequest.objects.create(
                customer=request.user,
                delivery_person=delivery_person,
                status='pending'
            )
            
            return JsonResponse({
                'status': 'success',
                'request_id': delivery_request.id,
                'message': 'Delivery request sent successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

class DeliveryRequestStatusView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        try:
            delivery_request = DeliveryRequest.objects.get(
                id=request_id,
                customer=request.user
            )
            
            return JsonResponse({
                'status': delivery_request.status,
                'delivery_person_name': delivery_request.delivery_person.username,
                'request_id': delivery_request.id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

class DeliveryHome(LoginRequiredMixin, View):
    def get(self, request):
        pending_requests = DeliveryRequest.objects.filter(
            delivery_person=request.user,
            status='pending'
        )
        return render(request, 'delivery/delivery_home.html', {
            'delivery_requests': pending_requests
        })