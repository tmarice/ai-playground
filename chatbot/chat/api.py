from typing import Optional

from django.contrib.auth.decorators import login_required
from django_bolt import BoltAPI, StreamingResponse
from django_bolt.exceptions import NotFound

from chat.models import Chat
from chat.redis import RedisStreamReader

api = BoltAPI(prefix="/api/v1", django_middleware=True)


@api.get("/chat/{chat_uuid}")
@login_required
async def chat_sse(request, chat_uuid: str, last_seq_id: Optional[int] = None):
    if not await Chat.objects.filter(uuid=chat_uuid, user_id=request.user_id).aexists():
        raise NotFound("Chat not found")

    stream_reader = RedisStreamReader(chat_uuid=chat_uuid, last_seq_id=last_seq_id)

    async def event_generator():
        async for message_chunk, seq_id in stream_reader.read():
            yield f"event: message\nid: {seq_id}\ndata: {message_chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
