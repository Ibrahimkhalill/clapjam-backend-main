from django.urls import path
from .views import alcoholbot_view, fetch_ai_chat

urlpatterns = [
    path('post/alcoholbot/', alcoholbot_view, name='alcoholbot'),
    path('get/fetch-ai-chat/', fetch_ai_chat, name='fetch_ai_chat'),
]