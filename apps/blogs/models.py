import logging

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _

from .markdown_utils import render_markdown

logger = logging.getLogger(__name__)


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
    views = models.PositiveIntegerField(_("Unique views"), default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return self.title

    def save(self, *args, auto_translate=None, **kwargs):
        # 1) Write once in any language → auto-fill the empty languages.
        if auto_translate is None:
            auto_translate = getattr(settings, "POST_AUTO_TRANSLATE", True)
        if auto_translate:
            try:
                from .translation import autofill_translations

                autofill_translations(
                    self,
                    provider=getattr(settings, "POST_TRANSLATE_PROVIDER", "google"),
                )
            except Exception:  # never block saving on a translation problem
                logger.exception("auto-translate failed for post %r", self.pk)

        # 2) Slug from the English title (filled by step 1) → clean ASCII; fall
        #    back to any title or the pk-less default if EN couldn't be produced.
        if not self.slug:
            base = (
                slugify(self.title)
                or slugify(self.title_ru, allow_unicode=False)
                or slugify(self.title_uz, allow_unicode=False)
                or "post"
            )
            candidate = base
            i = 2
            while Post.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate

        # 3) Render Markdown → HTML for every language.
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


class PostView(models.Model):
    """One row per unique visitor of a post.

    Authenticated users are keyed by their user id; anonymous visitors by a
    hash of IP + User-Agent. The unique constraint guarantees that repeated
    visits by the same person are not counted twice.
    """

    post = models.ForeignKey(Post, related_name="view_records", on_delete=models.CASCADE)
    visitor_key = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "visitor_key"], name="unique_post_visitor"
            )
        ]
        verbose_name = _("Post view")
        verbose_name_plural = _("Post views")

    def __str__(self):
        return f"{self.post_id}:{self.visitor_key}"


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
