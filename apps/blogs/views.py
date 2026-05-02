from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from .models import Post


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


class TechBlogDetailView(DetailView):
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


class PersonalBlogDetailView(PersonalAccessMixin, DetailView):
    template_name = "blogs/personal_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(
            category=Post.Category.PERSONAL, is_published=True
        )
