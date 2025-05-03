from django.forms import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *

class UserRegisterationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields
    
    def save():
        
        user = super().save(commit=False)
        user.role = 'customer'
        user.latitude = 0
        user.longitude = 0
        user.save()

class VendorRegisterationForm(UserCreationForm):
    class Meta:
        model = DeliveryUser
        fields = UserCreationForm.Meta.fields

class DeliveryRegisterationForm(UserCreationForm):
    class Meta:
        model = VendorUser
        fields = UserCreationForm.Meta.fields + ('cost_per_km')


