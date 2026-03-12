from .base import *

INSTALLED_APPS += [
    "django_bolt",
]

BOLT_APPLICATION = "chat.api.app"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "chatbot",
        "USER": "chatbot",
        "PASSWORD": "chatbot",
        "HOST": "db",
        "PORT": "5432",
        "OPTIONS": {"pooling": True},
    }
}
