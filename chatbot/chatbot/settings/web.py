from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "chatbot",
        "USER": "chatbot",
        "PASSWORD": "chatbot",
        "HOST": "db",
        "PORT": "5432",
        "OPTIONS": {},
    }
}


CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
]
