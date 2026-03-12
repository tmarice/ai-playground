import asyncio

from django.http import HttpResponse
from django.views.generic import TemplateView, View

from chat.models import Provider


class ChatView(View):
    async def get(self, request, uuid):
        await asyncio.sleep(1)  # Simulate some async work
        return HttpResponse(f"Hello, this is the {uuid} chat view!")


class NewChatView(TemplateView):
    template_name = "base.html"

    async def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_providers"] = [
            x
            async for x in Provider.objects.order_by("provider_type").values_list(
                "provider_type", flat=True
            )
        ]

        return context

    async def get(self, request, *args, **kwargs):
        context = await self.get_context_data(**kwargs)

        return self.render_to_response(context)
