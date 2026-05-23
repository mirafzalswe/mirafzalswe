from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from .forms import ContactForm
from .models import ContactMessage


class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = "contact/index.html"
    success_url = reverse_lazy("contact:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = self.object
        email = EmailMessage(
            subject=f"[mirafzal.dev] New message from {obj.name}",
            body=f"From: {obj.name} <{obj.email}>\n\n{obj.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[obj.email],
        )
        email.send(fail_silently=True)
        messages.success(
            self.request, _("Thanks — your message is in. I'll reply soon.")
        )
        return response
