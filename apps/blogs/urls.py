from django.urls import path

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.BlogIndexView.as_view(), name="index"),
    path("tech/", views.TechBlogListView.as_view(), name="tech_list"),
    path("tech/<slug:slug>/", views.TechBlogDetailView.as_view(), name="tech_detail"),
    path("personal/", views.PersonalBlogListView.as_view(), name="personal_list"),
    path(
        "personal/<slug:slug>/",
        views.PersonalBlogDetailView.as_view(),
        name="personal_detail",
    ),
]
