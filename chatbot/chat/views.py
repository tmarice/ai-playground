from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from chat.models import Chat, Message, Provider
from chat.tasks import process_user_message


@method_decorator(login_required, name="dispatch")
class ChatView(View):
    def get(self, request, uuid):
        return HttpResponse(f"Hello, this is the {uuid} chat view!")


@method_decorator(login_required, name="dispatch")
class NewChatView(TemplateView):
    template_name = "chat/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_providers"] = Provider.objects.order_by(
            "provider_type"
        ).values_list("provider_type", flat=True)

        return context

    def post(self, request, *args, **kwargs):
        selected_provider_type = request.POST.get("provider")
        provider = Provider.objects.get(
            user_id=request.user_id, provider_type=selected_provider_type
        )

        message = request.POST.get("message", "").strip()
        with transaction.atomic():
            chat = Chat.objects.create(
                user_id=request.user_id, title=message[:255], provider=provider
            )
            Message.objects.create(
                chat=chat,
                role=Message.Role.USER,
                content=message,
                status=Message.Status.DONE,
            )
            process_user_message.defer(chat.id)

        return render(
            request,
            "chat/newChatPartial.html",
            {
                "chat": chat,
                "message": message,
                "provider": provider,
            },
        )
