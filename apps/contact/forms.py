from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "message")
        labels = {
            "name": _("Name"),
            "email": _("Email"),
            "message": _("Message"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Your name")}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "message": forms.Textarea(
                attrs={"rows": 6, "placeholder": _("What's on your mind?")}
            ),
        }
