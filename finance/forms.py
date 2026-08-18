# finance/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Owner


class OwnerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Owner
        fields = UserCreationForm.Meta.fields