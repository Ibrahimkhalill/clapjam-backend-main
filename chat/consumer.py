from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import json
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self):
        if hasattr(self, 'chat_group_name'):
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            text = data.get('text')
            image_url = data.get('image_url')
            sender_id = data.get('sender_id')

            if not (text or image_url):
                await self.send(text_data=json.dumps({
                    "error": "At least one of text or image_url is required"
                }))
                return

            await self.save_message(text=text, image_url=image_url, sender_id=sender_id)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'sender_id': sender_id,
                        'text': text,
                        'image_url': image_url,
                        'created_at': await self.get_current_timestamp()
                    }
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON"
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                "error": str(e)
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, text: str, image_url: str, sender_id):
        from .models import Chat, ChatHistory
        user = User.objects.get(id=sender_id)
        print("chat_id",self.chat_id)
        chat = Chat.objects.get(id=self.chat_id)
        print("chat", chat)
        ChatHistory.objects.create(
            chat=chat,
            sender=user,
            text=text,
            image_url=image_url
        )

    @database_sync_to_async
    def get_current_timestamp(self):
        from django.utils import timezone
        return timezone.now().timestamp()
