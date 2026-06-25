from django import forms
from django.utils.translation import gettext_lazy as _

from apps.blogs.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title", "title_ru", "title_uz",
            "slug", "category",
            "excerpt", "excerpt_ru", "excerpt_uz",
            "content", "content_ru", "content_uz",
            "cover_image", "is_published",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "studio-input", "placeholder": "Post title (English)"}),
            "title_ru": forms.TextInput(attrs={"class": "studio-input", "placeholder": "Заголовок поста"}),
            "title_uz": forms.TextInput(attrs={"class": "studio-input", "placeholder": "Post sarlavhasi"}),
            "slug": forms.TextInput(attrs={"class": "studio-input", "placeholder": "auto-generated if empty"}),
            "category": forms.Select(attrs={"class": "studio-input"}),
            "excerpt": forms.Textarea(attrs={"class": "studio-input", "rows": 2, "placeholder": "Short summary for listings"}),
            "excerpt_ru": forms.Textarea(attrs={"class": "studio-input", "rows": 2, "placeholder": "Краткое описание"}),
            "excerpt_uz": forms.Textarea(attrs={"class": "studio-input", "rows": 2, "placeholder": "Qisqacha tavsif"}),
            "content": forms.Textarea(attrs={"id": "studio-content", "rows": 20, "required": False}),
            "content_ru": forms.Textarea(attrs={"id": "id_content_ru", "rows": 20, "required": False}),
            "content_uz": forms.Textarea(attrs={"id": "id_content_uz", "rows": 20, "required": False}),
        }

    # Languages you may author in — translations are filled automatically on save.
    _LANG_TITLES = ("title", "title_ru", "title_uz")
    _LANG_CONTENTS = ("content", "content_ru", "content_uz")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["is_published"].initial = True
        # Any single language is enough — the others are auto-translated, so no
        # individual title/excerpt/content field is required at the form level.
        for name in (*self._LANG_TITLES, *self._LANG_CONTENTS,
                     "excerpt", "excerpt_ru", "excerpt_uz"):
            self.fields[name].required = False

    def clean(self):
        cleaned = super().clean()
        has_title = any((cleaned.get(f) or "").strip() for f in self._LANG_TITLES)
        has_content = any((cleaned.get(f) or "").strip() for f in self._LANG_CONTENTS)
        if not (has_title and has_content):
            raise forms.ValidationError(
                _("Fill in the title and content in at least one language — "
                  "use the Translate button to fill the others.")
            )
        return cleaned
