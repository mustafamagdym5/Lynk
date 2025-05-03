from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


# Create your views here.
class HomeLocation(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'location/home_location.html', {})
    

class ChooseFromMap(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'location/choose_location.html', {})
    
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SaveLocation(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))

            print(f'Latitude: {latitude}, Longitude: {longitude}')
            
            user = request.user
            user.latitude = latitude
            user.longitude = longitude
            user.save()
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('home:home_page')
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)