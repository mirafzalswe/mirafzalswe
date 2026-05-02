from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .markdown_utils import render_markdown


class Post(models.Model):
    class Category(models.TextChoices):
        TECH = "tech", "Tech Blog"
        PERSONAL = "personal", "Personal Blog"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(
        max_length=16, choices=Category.choices, default=Category.TECH
    )
    excerpt = models.CharField(
        max_length=280,
        blank=True,
        help_text="Short summary shown in listings.",
    )
    content = models.TextField(help_text="Markdown source")
    content_html = models.TextField(blank=True, editable=False)
    cover_image = models.ImageField(upload_to="blog_covers/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "post"
            candidate = base
            i = 2
            while Post.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        self.content_html = render_markdown(self.content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.category == self.Category.TECH:
            return reverse("blogs:tech_detail", kwargs={"slug": self.slug})
        return reverse("blogs:personal_detail", kwargs={"slug": self.slug})


class MediaAsset(models.Model):
    class Kind(models.TextChoices):
        IMAGE = "image", "Image"
        STICKER = "sticker", "Sticker"

    name = models.CharField(max_length=120, blank=True)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.IMAGE)
    file = models.FileField(upload_to="assets/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or self.file.name

    @property
    def markdown_snippet(self) -> str:
        alt = self.name or "image"
        return f"![{alt}]({self.file.url})"
