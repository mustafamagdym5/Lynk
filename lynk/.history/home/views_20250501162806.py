from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from category.models import Category, Product
from users.models import CustomUser
from cart.models import Cart, CartProducts
from geopy.distance import geodesic
import math
from collections import defaultdict
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
        
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart).select_related('product__owner')
        
        # Group products by vendor
        vendor_products = defaultdict(list)
        for cart_product in cart_products:
            vendor_products[cart_product.product.owner].append(cart_product.product)
        
        # Get all unique vendor locations
        vendor_locations = []
        for vendor in vendor_products.keys():
            if vendor.latitude and vendor.longitude:
                vendor_locations.append((vendor.latitude, vendor.longitude))
        
        if not vendor_locations:
            # Handle case where no vendors have locations
            return render(request, 'customer/select_delivery.html', {
                'error': 'Product vendors have no location information'
            })
        
        user_location = (request.user.latitude, request.user.longitude)
        
        # Get available delivery persons
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
        
        delivery_list = []
        for delivery in deliveries:
            try:
                delivery_location = (delivery.latitude, delivery.longitude)
                
                # Calculate total delivery route distance
                total_distance = 0
                
                # 1. Distance from delivery person to first vendor
                first_vendor = vendor_locations[0]
                total_distance += geodesic(delivery_location, first_vendor).km
                
                # 2. Distances between vendors (if multiple vendors)
                for i in range(len(vendor_locations) - 1):
                    total_distance += geodesic(vendor_locations[i], vendor_locations[i+1]).km
                
                # 3. Distance from last vendor to customer
                last_vendor = vendor_locations[-1]
                total_distance += geodesic(last_vendor, user_location).km
                
                # Calculate estimated time (assuming 30 km/h average speed)
                estimated_time_min = math.ceil((total_distance / 30) * 60)
                
                # Calculate cost
                cost = (Decimal(str(total_distance)) * delivery.cost_per_km).quantize(Decimal('0.00'))
                
                delivery_list.append({
                    'delivery': delivery,
                    'distance_km': round(total_distance, 1),
                    'estimated_time_min': estimated_time_min,
                    'cost': cost,
                    'vendor_count': len(vendor_locations)
                })
                
            except Exception as e:
                print(f"Error processing delivery {delivery.id}: {str(e)}")
                continue
        
        # Sort by distance (shortest total route first)
        delivery_list.sort(key=lambda x: x['distance_km'])
        
        ctx = {
            'delivery_list': delivery_list,
            'user_location': user_location,
            'total_deliveries': deliveries.count(),
            'valid_deliveries': len(delivery_list)
        }
        return render(request, 'customer/select_delivery.html', ctx)