from django.urls import path

from . import views

app_name = "studio"

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("new/", views.post_create, name="post_create"),
    path("<int:pk>/edit/", views.post_edit, name="post_edit"),
    path("<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("preview/", views.preview, name="preview"),
    path("translate/", views.translate, name="translate"),
    path("upload/", views.upload, name="upload"),
    path("stickers/", views.stickers, name="stickers"),
    path("media/", views.media_library, name="media"),
]
