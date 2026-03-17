from typing import Optional

from django_bolt import BoltAPI
from django_bolt.exceptions import NotFound
from django_bolt.middleware import no_compress
from django_bolt.responses import StreamingResponse

from chat.models import Message
from chat.redis import RedisStreamReader

api = BoltAPI(prefix="/api/v1")


@api.get("/chat/{chat_uuid}/{message_uuid}")
@no_compress
async def chat_sse(
    request,
    chat_uuid: str,
    message_uuid: str,
    last_seq_id: Optional[str] = None,
):
    if last_seq_id is None:
        last_seq_id = "0"

    # user = await request.auser()
    # if not user.is_authenticated:
    #     raise NotFound()

    message = await Message.objects.filter(
        uuid=message_uuid,
        chat__uuid=chat_uuid,
        # chat__user=user,
    ).afirst()
    if message is None:
        raise NotFound()

    stream_reader = RedisStreamReader(
        message_uuid=message_uuid, last_seq_id=last_seq_id.strip()
    )

    async def event_generator():
        async for message_chunk, seq_id in stream_reader.read():
            yield f"event: message\nid: {seq_id}\ndata: {message_chunk}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
