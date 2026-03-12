from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from chat.models import Provider


@method_decorator(login_required, name="dispatch")
class ChatView(View):
    def get(self, request, uuid):
        return HttpResponse(f"Hello, this is the {uuid} chat view!")


@method_decorator(login_required, name="dispatch")
class NewChatView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_providers"] = Provider.objects.order_by(
            "provider_type"
        ).values_list("provider_type", flat=True)

        return context
