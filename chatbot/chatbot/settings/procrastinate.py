from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "chatbot",
        "USER": "chatbot",
        "PASSWORD": "chatbot",
        "HOST": "db",
        "PORT": "5432",
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "pool": {
                "min_size": 2,
                "max_size": 20,
            },
        },
    }
}

INSTALLED_APPS += [
    "procrastinate.contrib.django",
]
