from django.conf import settings


def site_settings(request):
    return {"site": settings.SITE_CONTENT}
