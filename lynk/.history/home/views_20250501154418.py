from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from category.models import Category, Product
from users.models import CustomUser
from geopy.distance import geodesic
import math
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.role == 'vendor':
            return redirect(reverse('vendor:vendor_home'))
        if request.user.is_authenticated and request.user.role == 'delivery':
            return redirect(reverse('delivery:delivery_home'))
        categories = Category.objects.all()
        products = Product.objects.all()
        ctx = {
            'categories': categories,
            'products': products,
        }
        if request.user.is_authenticated:
            print(request.user.latitude, request.user.longitude)
        return render(request, 'home/customer_home.html', ctx)


class SelectDelivery(LoginRequiredMixin, View):
    def get(self, request):
        # Debug: Print user location
        print(f"User location - Lat: {request.user.latitude}, Lon: {request.user.longitude}")
        
        if not request.user.latitude or not request.user.longitude:
            return redirect('location:choose_location')
        
        user_location = (request.user.latitude, request.user.longitude)
        deliveries = CustomUser.objects.filter(role='delivery').exclude(
            latitude__isnull=True
        ).exclude(
            longitude__isnull=True
        ).exclude(
            cost_per_km__isnull=True
        ).exclude(
            latitude=0
        ).exclude(
            longitude=0
        )
        
        print(f"Found {deliveries.count()} valid delivery persons")
        
        delivery_list = []
        for delivery in deliveries:
            try:
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
            except Exception as e:
                print(f"Error processing delivery {delivery.id}: {str(e)}")
                continue
        
        print(f"Processed {len(delivery_list)} deliveries for display")
        
        # Sort by distance (nearest first)
        delivery_list.sort(key=lambda x: x['distance_km'])
        
        ctx = {
            'delivery_list': delivery_list,
            'user_location': user_location,
            'total_deliveries': deliveries.count(),
            'valid_deliveries': len(delivery_list)
        }
        return render(request, 'customer/select_delivery.html', ctx)