from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import AccessRequest

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class AccessRequestForm(forms.ModelForm):
    class Meta:
        model = AccessRequest
        fields = ("reason",)
        widgets = {
            "reason": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Tell me a bit about why you'd like access…",
                }
            )
        }
