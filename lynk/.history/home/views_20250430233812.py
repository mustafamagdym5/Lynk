from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from category.models import Category, Product
from users.models import CustomUser
from geopy.distance import geodesic
import math
from decimal import Decimal

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


class SelectDelivery(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.latitude or not request.user.longitude:
            return redirect('location:choose_location')
        
        user_location = (request.user.latitude, request.user.longitude)
        deliveries = CustomUser.objects.filter(role='delivery')
        print(deliveries)
        
        delivery_list = []
        for delivery in deliveries:
            if delivery.latitude and delivery.longitude:
                delivery_location = (delivery.latitude, delivery.longitude)
                distance_km = geodesic(user_location, delivery_location).km
                
                # Calculate estimated time (assuming average speed of 30 km/h)
                estimated_time_min = math.ceil((distance_km / 30) * 60)
                
                # Calculate cost (using the delivery person's cost_per_km)
                cost = (Decimal(str(distance_km)) * delivery.cost_per_km).quantize(Decimal('0.00'))
                
                delivery_list.append({
                    'delivery': delivery,
                    'distance_km': round(distance_km, 1),
                    'estimated_time_min': estimated_time_min,
                    'cost': cost
                })
        
        # Sort by distance (nearest first)
        # delivery_list.sort(key=lambda x: x['distance_km'])
        
        ctx = {
            'delivery_list': delivery_list,
            'user_location': user_location
        }
        return render(request, 'customer/select_delivery.html', ctx)
