from django.shortcuts import render
from django.views import View
from .models import Cart, CartProducts
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class ViewCart(LoginRequiredMixin, View):
    def get(self, request)