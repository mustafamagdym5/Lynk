from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator


# Create your views here.
class HomeLocation(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'location/home_location.html', {})
    

class ChooseFromMap(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'location/choose_location.html', {})