from .base import *

# --- Development-specific settings ---

DEBUG = True

if not SECRET_KEY and DEBUG:
    # Use a placeholder key *only* for local development
    SECRET_KEY = "p1j+#gu-s^$6#k7bj4j+yg37ug6ggj4=m)(07&sl52!m908$ky"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.1.2"]

# --- Database ---
# Use local sqlite3 for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Email ---
# Use console backend for local development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- Logging ---
# Show all DEBUG messages in development
LOGGING["root"]["level"] = "DEBUG"

# --- Django Debug Toolbar ---
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# INTERNAL_IPS = ["192.168.1.2", "127.0.0.1"]