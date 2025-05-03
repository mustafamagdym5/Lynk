from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class VendorHome(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'vendor':
            return redirect(reverse('home:home_page'))
        return render(request, 'vendor/venfor_home.html', {})