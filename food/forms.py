# myapp/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Inform a valid email address.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
