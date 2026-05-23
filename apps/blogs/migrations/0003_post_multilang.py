from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogs", "0002_mediaasset_post_content_html_alter_post_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="title_ru",
            field=models.CharField(blank=True, max_length=200, verbose_name="Title (RU)"),
        ),
        migrations.AddField(
            model_name="post",
            name="title_uz",
            field=models.CharField(blank=True, max_length=200, verbose_name="Title (UZ)"),
        ),
        migrations.AddField(
            model_name="post",
            name="excerpt_ru",
            field=models.CharField(blank=True, max_length=280, verbose_name="Excerpt (RU)"),
        ),
        migrations.AddField(
            model_name="post",
            name="excerpt_uz",
            field=models.CharField(blank=True, max_length=280, verbose_name="Excerpt (UZ)"),
        ),
        migrations.AddField(
            model_name="post",
            name="content_ru",
            field=models.TextField(blank=True, verbose_name="Content (RU)"),
        ),
        migrations.AddField(
            model_name="post",
            name="content_uz",
            field=models.TextField(blank=True, verbose_name="Content (UZ)"),
        ),
        migrations.AddField(
            model_name="post",
            name="content_html_ru",
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AddField(
            model_name="post",
            name="content_html_uz",
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Title (EN)"),
        ),
        migrations.AlterField(
            model_name="post",
            name="excerpt",
            field=models.CharField(blank=True, help_text="Short summary shown in listings.", max_length=280, verbose_name="Excerpt (EN)"),
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.TextField(help_text="Markdown source", verbose_name="Content (EN)"),
        ),
        migrations.AlterField(
            model_name="post",
            name="cover_image",
            field=models.ImageField(blank=True, null=True, upload_to="blog_covers/", verbose_name="Cover image"),
        ),
        migrations.AlterField(
            model_name="post",
            name="is_published",
            field=models.BooleanField(default=True, verbose_name="Published"),
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.CharField(choices=[("tech", "Tech Blog"), ("personal", "Personal Blog")], default="tech", max_length=16, verbose_name="Category"),
        ),
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-created_at"], "verbose_name": "Post", "verbose_name_plural": "Posts"},
        ),
        migrations.AlterField(
            model_name="mediaasset",
            name="name",
            field=models.CharField(blank=True, max_length=120, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="mediaasset",
            name="kind",
            field=models.CharField(choices=[("image", "Image"), ("sticker", "Sticker")], default="image", max_length=16, verbose_name="Kind"),
        ),
        migrations.AlterField(
            model_name="mediaasset",
            name="file",
            field=models.FileField(upload_to="assets/%Y/%m/", verbose_name="File"),
        ),
        migrations.AlterModelOptions(
            name="mediaasset",
            options={"ordering": ["-created_at"], "verbose_name": "Media asset", "verbose_name_plural": "Media assets"},
        ),
    ]
