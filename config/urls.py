from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls", namespace="pages")),
    path("blogs/", include("apps.blogs.urls", namespace="blogs")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("contacts/", include("apps.contact.urls", namespace="contact")),
    path("studio/", include("apps.studio.urls", namespace="studio")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
