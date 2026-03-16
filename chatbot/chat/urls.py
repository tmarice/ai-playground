from django.urls import path

from chat.views import ChatView, NewChatView

urlpatterns = [
    path("", NewChatView.as_view(), name="new_chat"),
    path("<uuid:chat_uuid>", ChatView.as_view(), name="chat_detail"),
]
