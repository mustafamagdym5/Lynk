from django import forms
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
        model = CustomUser
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
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'cost_per_km')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'delivery'
        user.latitude = 0
        user.longitude = 0
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput)

