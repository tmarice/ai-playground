import uuid

from django.db import models


class Provider(models.Model):
    class ProviderType(models.TextChoices):
        OPENAI = "OpenAI"
        ANTHROPIC = "Anthropic"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    provider_type = models.CharField(choices=ProviderType, max_length=255)
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.provider_type} Provider"


class Chat(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Chat {self.timestamp}"

    def dump_messages_list(self):
        messages = self.message_set.order_by("created_at").values("role", "content")
        messages_list = [
            {
                "role": m["role"],
                "content": m["content"],
            }
            for m in messages
        ]
        return messages_list


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    role = models.CharField(choices=Role, max_length=255)
    content = models.TextField()
    last_consumed_seq_id = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=Status, max_length=255, default=Status.PENDING)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
