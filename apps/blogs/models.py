from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _

from .markdown_utils import render_markdown


class Post(models.Model):
    class Category(models.TextChoices):
        TECH = "tech", _("Tech Blog")
        PERSONAL = "personal", _("Personal Blog")

    title = models.CharField(_("Title (EN)"), max_length=200)
    title_ru = models.CharField(_("Title (RU)"), max_length=200, blank=True)
    title_uz = models.CharField(_("Title (UZ)"), max_length=200, blank=True)

    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(
        _("Category"),
        max_length=16, choices=Category.choices, default=Category.TECH,
    )

    excerpt = models.CharField(
        _("Excerpt (EN)"),
        max_length=280,
        blank=True,
        help_text=_("Short summary shown in listings."),
    )
    excerpt_ru = models.CharField(_("Excerpt (RU)"), max_length=280, blank=True)
    excerpt_uz = models.CharField(_("Excerpt (UZ)"), max_length=280, blank=True)

    content = models.TextField(_("Content (EN)"), help_text=_("Markdown source"))
    content_ru = models.TextField(_("Content (RU)"), blank=True)
    content_uz = models.TextField(_("Content (UZ)"), blank=True)

    content_html = models.TextField(blank=True, editable=False)
    content_html_ru = models.TextField(blank=True, editable=False)
    content_html_uz = models.TextField(blank=True, editable=False)

    cover_image = models.ImageField(_("Cover image"), upload_to="blog_covers/", blank=True, null=True)
    is_published = models.BooleanField(_("Published"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

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
        self.content_html_ru = render_markdown(self.content_ru)
        self.content_html_uz = render_markdown(self.content_uz)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.category == self.Category.TECH:
            return reverse("blogs:tech_detail", kwargs={"slug": self.slug})
        return reverse("blogs:personal_detail", kwargs={"slug": self.slug})

    def _localized(self, base_attr: str) -> str:
        """Return the field value for the active language, falling back to EN."""
        lang = (get_language() or "en").split("-")[0]
        if lang in {"ru", "uz"}:
            value = getattr(self, f"{base_attr}_{lang}", "") or ""
            if value:
                return value
        return getattr(self, base_attr, "") or ""

    @property
    def display_title(self) -> str:
        return self._localized("title")

    @property
    def display_excerpt(self) -> str:
        return self._localized("excerpt")

    @property
    def display_content(self) -> str:
        return self._localized("content")

    @property
    def display_content_html(self) -> str:
        return self._localized("content_html")


class MediaAsset(models.Model):
    class Kind(models.TextChoices):
        IMAGE = "image", _("Image")
        STICKER = "sticker", _("Sticker")

    name = models.CharField(_("Name"), max_length=120, blank=True)
    kind = models.CharField(_("Kind"), max_length=16, choices=Kind.choices, default=Kind.IMAGE)
    file = models.FileField(_("File"), upload_to="assets/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Media asset")
        verbose_name_plural = _("Media assets")

    def __str__(self):
        return self.name or self.file.name

    @property
    def markdown_snippet(self) -> str:
        alt = self.name or "image"
        return f"![{alt}]({self.file.url})"
