from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import AccessRequest

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label=_("Email"), required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": _("Username"),
        }


class AccessRequestForm(forms.ModelForm):
    class Meta:
        model = AccessRequest
        fields = ("reason",)
        labels = {
            "reason": _("Reason"),
        }
        widgets = {
            "reason": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": _("Tell me a bit about why you'd like access…"),
                }
            )
        }
