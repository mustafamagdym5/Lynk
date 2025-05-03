from django.shortcuts import render
from django.views import View
from .forms import RegisterationForm

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
    def get(self, request):
        form = self.form()
        ctx = {
            'form':form
        }
        return render(request,'users/register.html', ct)
    

class RegisterVendor(View):
    def get(self, request):
        return render(request,'users/register.html', {})
    

class RegisterDelivery(View):
    def get(self, request):
        return render(request,'users/register.html', {})