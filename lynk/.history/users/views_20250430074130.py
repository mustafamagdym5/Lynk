from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView

# Create your views here.
class HomeUser(View):
    def get(self, request):
        return render(request, 'users/users_home.html', {})
    

class LoginView(LoginView):
    template_name = 'users/login.html'
    form = LoginForm
    def get(self, request):
        form = self.form
        ctx = {
            'form': form
        }
        return render(request, 'users/login.html', ctx)
    
    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect(reverse('home:home_page'))
        ctx = {
            'form': form,
            'error': 'Check Your Username and Password'
        }
        return render(request, 'users/login.html', ctx)

class LogoutView(View):
    def get(self, request):
        return render(request, 'users/logout.html', {})
    
    def post(self, request):
        logout(request)
        return redirect(reverse('users:login'))
    

class RegisterHome(View):
    def get(self, request):
        return render(request,'users/register_home.html', {})
    

class RegisterCustomer(View):
    form = UserRegisterationForm
    template = 'users/register.html'
    success_url = 'home:home_page'

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
            username = request.cleaned_data.get('username')
            password = request.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect(reverse(self.success_url))
        return render(request,self.template, ctx)
    
    
class RegisterVendor(View):
    form_class = VendorRegisterationForm
    template_name = 'users/register.html'
    success_url = 'vendor:vendor_home'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            username = request.POST.get('username')
            password = request.POST.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('vendor:vendor_home'))
        return render(request, self.template_name, {'form': form})    

class RegisterDelivery(View):
    form = DeliveryRegisterationForm