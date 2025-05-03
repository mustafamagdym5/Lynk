from django.forms import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

class RegisterationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role', 'latitude', 'longitude')
