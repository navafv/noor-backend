from .base import *
import dj_database_url

# --- Production-specific settings ---

DEBUG = os.getenv("DJANGO_DEBUG", "0").lower() in ("true", "1")

if not SECRET_KEY and not DEBUG:
    raise ValueError("DJANGO_SECRET_KEY must be set in production")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "your.domain.com").split(",")

# --- Database ---
# Uses dj_database_url to parse DATABASE_URL env var.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set for production")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=os.getenv("DATABASE_SSL_REQUIRE", "0") == "1"
    )
}

# --- Static & Media Files ---
# Use Whitenoise for static file serving in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Email ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "no-reply@noorinstitute.com")

# --- Production Security ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Sentry (Optional Error Tracking) ---
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.2,
        send_default_pii=True
    )