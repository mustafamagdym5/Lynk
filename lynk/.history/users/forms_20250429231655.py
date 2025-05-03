from django.forms import forms
from .models import CustomUser

class RegisterationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
