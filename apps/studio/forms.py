from django import forms

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["is_published"].initial = True
