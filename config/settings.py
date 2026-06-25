import os
from pathlib import Path

# Load .env file
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _val = _line.partition("=")
                os.environ.setdefault(_key.strip(), _val.strip())
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-change-me-in-production-7#t8@(h($ok2w)48scg3ql^*z",
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]




# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.pages",
    "apps.blogs",
    "apps.accounts",
    "apps.contact",
    "apps.studio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.pages.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.environ.get("DB_USER", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
    ("uz", _("Uzbek")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# Auto-translation of posts: write in one language, the rest are filled in on
# save. Set POST_AUTO_TRANSLATE=False to disable; provider: google|mymemory|deepl.
POST_AUTO_TRANSLATE = os.environ.get("POST_AUTO_TRANSLATE", "True") == "True"
POST_TRANSLATE_PROVIDER = os.environ.get("POST_TRANSLATE_PROVIDER", "google")

LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Auth redirects
# ---------------------------------------------------------------------------

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"

# ---------------------------------------------------------------------------
# Security (production)
# ---------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    h.strip()
    for h in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if h.strip()
]

if not DEBUG:
    # Enable these only after SSL/HTTPS is configured
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    pass

# ---------------------------------------------------------------------------
# Site content
# ---------------------------------------------------------------------------

SITE_CONTENT = {
    "owner_name": "Mirafzal Bakhodirov",
    "owner_tagline": "Founder | Developer | Startup Enthusiast",
    "owner_email": "mirafzalswe@gmail.com",
    "services_external_url": "https://abuali.uz/",
    "social_links": {
        "linkedin": "https://www.linkedin.com/in/mirafzal-bakhodirov/",
        "telegram": "https://t.me/MBswe",
        "instagram": "https://www.instagram.com/bakhodirov_mirafzal/",
        "youtube": "https://youtube.com/@mirafzal",
        "buymeacoffee": "https://buymeacoffee.com/mirafzal",
    },
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "mirafzalswe@gmail.com")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@mirafzal.dev")

_default_email_backend = (
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", _default_email_backend)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
