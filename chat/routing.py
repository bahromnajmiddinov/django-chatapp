from django.urls import path

from . import consumers

ASGI_urlpatterns = [
    path('websocket/private/<user_id>', consumers.ChatConsumer.as_asgi()),
    path('websocket/public-group/<group_username>', consumers.PublicGroupChatConsumer.as_asgi()),
    path('websocket/private-group/<group_username>', consumers.PrivateGroupChatConsumer.as_asgi()),
]
