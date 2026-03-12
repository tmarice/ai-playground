from django_bolt import BoltAPI

from chat.api import api as chat_api

api = BoltAPI()

api.mount_django("/app")
api.mount("/api/v1", chat_api)
