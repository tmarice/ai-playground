import redis.asyncio as redis
from django.conf import settings

STREAM_KEY_TEMPLATE = "message:{message_uuid}"
DONE_MARKER = "47d5eebe-7793-4e6e-a6e3-b62ec059e48f__done__"


class RedisStreamWriter:
    EXPIRATION_SECONDS = 60 * 10  # 10 minutes

    def __init__(self, message_uuid):
        self._message_uuid = message_uuid
        self._stream_key = STREAM_KEY_TEMPLATE.format(message_uuid=message_uuid)
        self._redis = redis.Redis.from_url(settings.REDIS_STREAMS_URL)

    async def write(self, message_chunk):
        seq_id = await self._redis.xadd(self._stream_key, {"c": message_chunk})

        return seq_id

    async def mark_done(self):
        await self._redis.xadd(self._stream_key, {"c": DONE_MARKER})
        await self._redis.expire(self._stream_key, self.EXPIRATION_SECONDS)


class RedisStreamReader:
    BLOCK_TIMEOUT_MS = 1000
    COUNT = 10

    def __init__(self, message_uuid, last_seq_id=0):
        self._message_uuid = message_uuid
        self._stream_key = STREAM_KEY_TEMPLATE.format(message_uuid=message_uuid)
        self._redis = redis.Redis.from_url(settings.REDIS_STREAMS_URL)
        self.last_seq_id = last_seq_id

    async def read(self):
        while True:
            response = await self._redis.xread(
                {self._stream_key: self.last_seq_id},
                block=self.BLOCK_TIMEOUT_MS,
                count=self.COUNT,
            )

            if not response:
                continue

            chunks = response[0][1]
            for seq_id, message_data in chunks:
                message_chunk = message_data[b"c"].decode("utf-8")

                if message_chunk == DONE_MARKER:
                    return

                self.last_seq_id = seq_id.decode("utf-8")
                # TODO Should I concatenate all chunks and yield them together?
                yield message_chunk, self.last_seq_id
