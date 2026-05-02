import os
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_POST

from apps.blogs.markdown_utils import render_markdown
from apps.blogs.models import MediaAsset, Post

from .forms import PostForm


def _is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


staff_only = user_passes_test(_is_staff, login_url="accounts:login")


@login_required
@staff_only
def post_list(request):
    posts = Post.objects.all().order_by("-updated_at")
    return render(request, "studio/post_list.html", {"posts": posts})


@login_required
@staff_only
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            messages.success(request, f"Post «{post.title}» created.")
            return redirect("studio:post_edit", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "studio/post_form.html", {"form": form, "post": None})


@login_required
@staff_only
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, "Saved.")
            return redirect("studio:post_edit", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "studio/post_form.html", {"form": form, "post": post})


@login_required
@staff_only
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("studio:post_list")


@login_required
@staff_only
@require_POST
def preview(request):
    return JsonResponse({"html": render_markdown(request.POST.get("content", ""))})


@login_required
@staff_only
@require_POST
def upload(request):
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("No file")
    kind = request.POST.get("kind") or "image"
    if kind not in dict(MediaAsset.Kind.choices):
        kind = "image"
    safe_name = get_valid_filename(f.name)
    base, ext = os.path.splitext(safe_name)
    asset = MediaAsset(name=base[:120], kind=kind)
    asset.file.save(f"{base}-{uuid4().hex[:8]}{ext}", f, save=True)
    return JsonResponse(
        {
            "id": asset.id,
            "url": asset.file.url,
            "markdown": asset.markdown_snippet,
            "name": asset.name,
            "kind": asset.kind,
        }
    )


@login_required
@staff_only
def stickers(request):
    items = [
        {"id": a.id, "url": a.file.url, "markdown": a.markdown_snippet, "name": a.name}
        for a in MediaAsset.objects.filter(kind=MediaAsset.Kind.STICKER)[:200]
    ]
    return JsonResponse({"items": items})


@login_required
@staff_only
def media_library(request):
    assets = MediaAsset.objects.all()
    return render(request, "studio/media.html", {"assets": assets})
