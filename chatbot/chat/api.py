from django_bolt import BoltAPI

api = BoltAPI(prefix="/api/v1")


@api.get("/hello")
async def hello():
    return {"message": "Hello, World!"}
