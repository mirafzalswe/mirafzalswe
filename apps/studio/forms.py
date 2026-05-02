from django import forms

from apps.blogs.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "slug", "category", "excerpt", "content", "cover_image", "is_published")
        widgets = {
            "title": forms.TextInput(attrs={"class": "studio-input", "placeholder": "Post title"}),
            "slug": forms.TextInput(attrs={"class": "studio-input", "placeholder": "auto-generated if empty"}),
            "category": forms.Select(attrs={"class": "studio-input"}),
            "excerpt": forms.Textarea(attrs={"class": "studio-input", "rows": 2, "placeholder": "Short summary for listings"}),
            "content": forms.Textarea(attrs={"id": "studio-content", "rows": 20, "required": False}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["is_published"].initial = True
