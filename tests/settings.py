SECRET_KEY = "tests"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "modeltrans",
    "modeltrans_tabs",
    "tests",
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("fr", "French"), ("de", "German"), ("it", "Italian")]
STATIC_URL = "/static/"
USE_TZ = True
