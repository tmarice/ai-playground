from chat.models import Provider


async def process_anthropic_message(messages):
    # Placeholder for processing messages with Anthropic provider
    pass


async def process_openai_message(messages):
    # Placeholder for processing messages with Anthropic provider
    pass


PROVIDER_HANDLERS = {
    Provider.ProviderType.OPENAI: process_openai_message,
    Provider.ProviderType.ANTHROPIC: process_anthropic_message,
}
