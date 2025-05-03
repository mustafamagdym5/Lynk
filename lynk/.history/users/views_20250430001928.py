from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import RegisterationForm
from django.contrib.auth import authenticate, login

# Create your views here.
class HomeUser(View):
    def get(self, request):
        return render(request, 'users/users_home.html', {})
    

class LoginView(View):
    def get(self, request):
        return render(request,'users/login.html', {})
    

class LogoutView(View):
    def get(self, request):
        return render(request, 'users/logout.html', {})
    

class RegisterHome(View):
    def get(self, request):
        return render(request,'users/register_home.html', {})
    

class RegisterCustomer(View):
    form = RegisterationForm
    template = 'users/register.html'
    role = 'customer'

    def get(self, request):
        form = self.form()
        ctx = {
            'form':form
        }
        return render(request,self.template, ctx)
    
    def post(self, request):
        form = self.form(request.POST)
        ctx = {
            'form':form,
        }
        if form.is_valid():
            user = form.save()
            login(request, user)
            return red

    
    

class RegisterVendor(View):
    def get(self, request):
        return render(request,'users/register.html', {})
    

class RegisterDelivery(View):
    def get(self, request):
        return render(request,'users/register.html', {})