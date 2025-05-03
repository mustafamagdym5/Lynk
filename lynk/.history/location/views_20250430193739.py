from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
class HomeLocation(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'location/home_location.html', {})
    

class ChooseFromMap(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'location/choose_location.html', {})
    
class SaveLocation(LoginRequiredMixin, View):
    def post(self, request):
        try:
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            
            user = request.user
            user.latitude = latitude
            user.longitude = longitude
            user.save()
            
            messages.success(request, 'Your location has been saved successfully!')
            return redirect('home:home_page')
            
        except Exception as e:
            messages.error(request, f'Error saving location: {str(e)}')
            return redirect('location:choose_from_map')