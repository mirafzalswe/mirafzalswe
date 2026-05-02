from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView

from .forms import AccessRequestForm, SignUpForm
from .models import AccessRequest


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:request_access")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            "Account created. You can now request access to personal blogs.",
        )
        return response


class RequestAccessView(LoginRequiredMixin, FormView):
    form_class = AccessRequestForm
    template_name = "accounts/request_access.html"
    success_url = reverse_lazy("blogs:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)
            if profile and profile.has_personal_access:
                return redirect("blogs:personal_list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pending_request"] = AccessRequest.objects.filter(
            user=self.request.user, status=AccessRequest.Status.PENDING
        ).first()
        return ctx

    def form_valid(self, form):
        existing = AccessRequest.objects.filter(
            user=self.request.user, status=AccessRequest.Status.PENDING
        ).first()
        if existing:
            messages.info(self.request, "You already have a pending request.")
            return redirect(self.success_url)

        access_request = form.save(commit=False)
        access_request.user = self.request.user
        access_request.save()

        profile = self.request.user.profile
        profile.access_requested_at = timezone.now()
        profile.save(update_fields=["access_requested_at"])

        messages.success(
            self.request,
            "Request submitted. You'll get access once it's approved.",
        )
        return super().form_valid(form)
