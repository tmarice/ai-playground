from django_bolt import BoltAPI

api = BoltAPI(prefix="/api")

api.mount_django("/", clear_root_path=True)
