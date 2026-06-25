import hashlib

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from .models import Post, PostView


def _visitor_key(request) -> str:
    """Stable identifier for a visitor used to deduplicate views."""
    if request.user.is_authenticated:
        return f"u{request.user.pk}"
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
    ua = request.META.get("HTTP_USER_AGENT", "")
    return hashlib.sha256(f"{ip}|{ua}".encode("utf-8")).hexdigest()[:64]


class RecordUniqueViewMixin:
    """Count one view per unique visitor for the post being displayed."""

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        post = getattr(self, "object", None)
        if post is not None:
            _, created = PostView.objects.get_or_create(
                post=post, visitor_key=_visitor_key(request)
            )
            if created:
                Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
        return response


class BlogIndexView(TemplateView):
    template_name = "blogs/index.html"


class TechBlogListView(ListView):
    template_name = "blogs/tech_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            category=Post.Category.TECH, is_published=True
        )


class TechBlogDetailView(RecordUniqueViewMixin, DetailView):
    template_name = "blogs/tech_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(
            category=Post.Category.TECH, is_published=True
        )


class PersonalAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        profile = getattr(request.user, "profile", None)
        if not (profile and profile.has_personal_access) and not request.user.is_superuser:
            return HttpResponseRedirect(reverse("accounts:request_access"))
        return super().dispatch(request, *args, **kwargs)


class PersonalBlogListView(PersonalAccessMixin, ListView):
    template_name = "blogs/personal_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            category=Post.Category.PERSONAL, is_published=True
        )


class PersonalBlogDetailView(PersonalAccessMixin, RecordUniqueViewMixin, DetailView):
    template_name = "blogs/personal_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(
            category=Post.Category.PERSONAL, is_published=True
        )
