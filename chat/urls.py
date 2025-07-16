from django.urls import path
from .views import alcoholbot_view, fetch_ai_chat
from .consumer import ChatConsumer
from .ChatImageAPI import *
from .ChatMessageAPI import *
urlpatterns = [
    path('post/alcoholbot/', alcoholbot_view, name='alcoholbot'),
    path('get/fetch-ai-chat/', fetch_ai_chat, name='fetch_ai_chat'),

    # user chat
    path('images/', ChatImageAPI.as_view(), name='chat-image-upload'),
    path('messages/<str:chat_id>/', ChatMessageAPI.as_view(), name='chat-messages'),
    path('create/', ChatAPI.as_view(), name='chat-create'),
    path('list/', UserChatsAPI.as_view(), name='chat-create'),
]


websocket_urlpatterns = [
    path('ws/chat/<uuid:chat_id>/', ChatConsumer.as_asgi(), name='chat_ws'),
]