from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class HomeLocation(LoginRequiredMixin, View):
    def get(self, request):
        pass