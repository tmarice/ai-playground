from openai import AsyncOpenAI, DefaultAioHttpClient

from chat.models import Provider


async def process_anthropic_message(provider, messages):
    # Placeholder for processing messages with Anthropic provider
    pass


CHUNK_DELTA_TYPE = "response.output_text.delta"


async def process_openai_message(provider, messages):
    async with AsyncOpenAI(
        api_key=provider.api_key,
        http_client=DefaultAioHttpClient(),
    ) as client:
        stream = await client.responses.create(
            model="gpt-5.2", input=messages, stream=True
        )

        async for chunk in stream:
            if chunk.type == CHUNK_DELTA_TYPE:
                yield chunk.delta


PROVIDER_HANDLERS = {
    Provider.ProviderType.OPENAI: process_openai_message,
    Provider.ProviderType.ANTHROPIC: process_anthropic_message,
}
