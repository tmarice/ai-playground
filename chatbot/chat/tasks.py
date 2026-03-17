from asgiref.sync import sync_to_async
from django.db.models import F, Value
from django.db.models.functions import Concat
from procrastinate.contrib.django import app as procrastinate_app

from chat.models import Message
from chat.providers import PROVIDER_HANDLERS
from chat.redis import RedisStreamWriter

SAVE_BATCH_SIZE = 50


@procrastinate_app.task
async def build_assistant_message(message_id):
    assistant_message = await Message.objects.select_related("chat__provider").aget(
        id=message_id
    )
    assistant_message.status = Message.Status.PROCESSING
    await assistant_message.asave(update_fields=["status"])

    stream_writer = RedisStreamWriter(message_uuid=assistant_message.uuid)
    provider_handler = PROVIDER_HANDLERS[assistant_message.chat.provider.provider_type]
    chunk_buffer = []
    messages_list = await sync_to_async(assistant_message.chat.dump_messages_list)()
    async for message_chunk in provider_handler(
        provider=assistant_message.chat.provider, messages=messages_list
    ):
        seq_id = (await stream_writer.write(message_chunk)).decode("utf-8")
        chunk_buffer.append(message_chunk)

        if len(chunk_buffer) >= SAVE_BATCH_SIZE:
            message_update = "".join(chunk_buffer)
            chunk_buffer = []
            await Message.objects.filter(id=assistant_message.id).aupdate(
                content=Concat(F("content"), Value(message_update)),
                last_seq_id=seq_id,
            )

    message_update = "".join(chunk_buffer)
    await Message.objects.filter(id=assistant_message.id).aupdate(
        status=Message.Status.DONE,
        content=Concat(F("content"), Value(message_update)),
        last_seq_id=seq_id,
    )

    await stream_writer.mark_done()
