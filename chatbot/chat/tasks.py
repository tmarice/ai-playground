import redis.asyncio as redis
from django.conf import settings
from django.db.models import F
from procrastinate.contrib.django import app

from chat.models import Chat, Message
from chat.providers import PROVIDER_HANDLERS

SAVE_BATCH_SIZE = 50


@app.task
async def process_user_message(chat_id):
    chat = await Chat.objects.select_related("provider").aget(id=chat_id)

    redis_client = redis.Redis(settings.REDIS_STREAMS_URL)

    stream_key = f"chat:{chat.uuid}:messages"
    provider_handler = PROVIDER_HANDLERS[chat.provider.provider_type]

    assistant_message = Message.objects.create(
        chat=chat,
        role=Message.Role.ASSISTANT,
        content="",
        status=Message.Status.PROCESSING,
    )

    seq_id = 0
    chunk_buffer = []
    messages_list = chat.dump_messages_list()
    async for message_chunk in provider_handler(messages_list):
        await redis_client.xadd(
            stream_key, {"message": message_chunk, "seq_id": seq_id}
        )
        seq_id += 1
        chunk_buffer.append(message_chunk)

        if seq_id % SAVE_BATCH_SIZE == 0:
            message_update = "".join(chunk_buffer)
            chunk_buffer = []
            await Message.objects.filter(id=assistant_message.id).aupdate(
                content=F("content") + message_update,
                last_consumed_seq_id=seq_id,
            )

    message_update = "".join(chunk_buffer)
    await Message.objects.filter(id=assistant_message.id).aupdate(
        status=Message.Status.DONE,
        content=F("content") + message_update,
        last_consumed_seq_id=seq_id,
    )
