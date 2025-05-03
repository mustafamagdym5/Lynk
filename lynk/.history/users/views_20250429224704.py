from django.shortcuts import render
from django.views import View

# Create your views here.
class HomeUser(View):
    def get(self, request):
        return render(request, 'users/users_home.html', {})