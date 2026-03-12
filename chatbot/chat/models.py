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
    providers = models.ManyToManyField(Provider)
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Chat {self.timestamp}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        Provider, on_delete=models.SET_NULL, null=True, blank=True
    )
    role = models.CharField(choices=Role, max_length=255)
    content = models.TextField()
    last_seq_id = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
