from django.contrib import admin

from chat.models import Chat, Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("provider_type", "api_key", "user")
    search_fields = ("provider_type",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "user")
    search_fields = ("id",)
    filter_horizontal = ("providers",)
