from django.forms import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *

class UserRegisterationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.latitude = 0
        user.longitude = 0
        if commit:
            user.save()
        return user

class VendorRegisterationForm(UserCreationForm):
    class Meta:
        model = DeliveryUser
        fields = UserCreationForm.Meta.fields
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'vendor'
        user.latitude = 0
        user.longitude = 0
        if commit:
            user.save()
        return user

class DeliveryRegisterationForm(UserCreationForm):
    class Meta:
        model = VendorUser
        fields = UserCreationForm.Meta.fields + ('cost_per_km',)

        def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.latitude = 0
        user.longitude = 0
        if commit:
            user.save()
        return user


