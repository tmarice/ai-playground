from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View

from chat.models import Chat, Message, Provider
from chat.tasks import build_assistant_message


@method_decorator(login_required, name="dispatch")
class ChatView(View):
    def get(self, request, chat_uuid):
        chat = get_object_or_404(Chat, uuid=chat_uuid, user_id=request.user.id)
        messages = list(chat.message_set.order_by("created_at"))
        last_seq_id = (
            messages[-1].last_seq_id
            if messages and messages[-1].status == Message.Status.PROCESSING
            else None
        )

        context = {
            "chat": chat,
            "chat_uuid": chat.uuid,
            "messages": messages,
            "last_seq_id": last_seq_id,
            "available_providers": Provider.objects.order_by(
                "provider_type"
            ).values_list("provider_type", flat=True),
        }

        return render(request, "chat/chat.html", context)

    def post(self, request, chat_uuid):
        chat = get_object_or_404(Chat, uuid=chat_uuid, user_id=request.user.id)
        message = request.POST.get("message", "").strip()
        with transaction.atomic():
            user_message = Message.objects.create(
                chat=chat,
                role=Message.Role.USER,
                content=message,
                status=Message.Status.DONE,
            )
            assistant_message = Message.objects.create(
                chat=chat,
                role=Message.Role.ASSISTANT,
                content="",
                status=Message.Status.PENDING,
            )
            build_assistant_message.defer(message_id=assistant_message.id)

        return render(
            request,
            "chat/messagePartial.html",
            {
                "chat": chat,
                "user_message": user_message,
                "assistant_message": assistant_message,
            },
        )


@method_decorator(login_required, name="dispatch")
class NewChatView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "available_providers": Provider.objects.order_by(
                "provider_type"
            ).values_list("provider_type", flat=True)
        }

        return render(request, "chat/chat.html", context)

    def post(self, request, *args, **kwargs):
        selected_provider_type = request.POST.get("provider")
        provider = Provider.objects.get(
            user_id=request.user.id, provider_type=selected_provider_type
        )

        message = request.POST.get("message", "").strip()
        with transaction.atomic():
            chat = Chat.objects.create(
                user_id=request.user.id, title=message[:255], provider=provider
            )
            user_message = Message.objects.create(
                chat=chat,
                role=Message.Role.USER,
                content=message,
                status=Message.Status.DONE,
            )
            assistant_message = Message.objects.create(
                chat=chat,
                role=Message.Role.ASSISTANT,
                content="",
                status=Message.Status.PENDING,
            )
            build_assistant_message.defer(message_id=assistant_message.id)

        response = render(
            request,
            "chat/newChatPartial.html",
            {
                "chat": chat,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "provider": provider,
            },
        )
        response["HX-Push-Url"] = reverse(
            "chat:chat_detail", kwargs={"chat_uuid": chat.uuid}
        )
        return response
