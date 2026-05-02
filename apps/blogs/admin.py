from django.contrib import admin
from django.utils.html import format_html

from .models import MediaAsset, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "content", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "is_published")}),
        ("Content", {"fields": ("excerpt", "content", "cover_image")}),
    )

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css",
                "css/admin_editor.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js",
            "js/admin_editor.js",
        )


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "kind", "markdown", "created_at")
    list_filter = ("kind", "created_at")
    search_fields = ("name",)
    readonly_fields = ("markdown_preview",)

    def preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-height:48px;max-width:96px;border-radius:4px;" />',
                obj.file.url,
            )
        return "—"

    preview.short_description = "Preview"

    def markdown(self, obj):
        return format_html(
            '<code style="user-select:all;font-size:11px;">{}</code>',
            obj.markdown_snippet,
        )

    markdown.short_description = "Markdown (copy)"

    def markdown_preview(self, obj):
        if not obj.pk:
            return "—"
        return format_html(
            '<textarea readonly style="width:100%;height:60px;">{}</textarea>',
            obj.markdown_snippet,
        )
