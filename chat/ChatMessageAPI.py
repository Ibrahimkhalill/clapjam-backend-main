
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import logging
from django.db import models
logger = logging.getLogger(__name__)

class ChatMessageAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, chat_id) -> Response:
        try:
            chat = Chat.objects.filter(
                id=chat_id,
                user1=request.user
            ).first() or Chat.objects.filter(
                id=chat_id,
                user2=request.user
            ).first()
            if not chat:
                return Response(
                    {"error": "Chat not found or you are not a participant"},
                    status=status.HTTP_404_NOT_FOUND
                )

            messages = chat.messages.all()
            return Response(
                {
                    "chat_id": str(chat.id),
                    "messages": [
                        {
                            "sender_id": msg.sender.id,
                            "content": msg.content,
                            "is_image": msg.is_image,
                            "created_at": msg.created_at.timestamp()
                        } for msg in messages
                    ]
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error fetching chat messages: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class UserChatsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        try:
            # Get all chats where the user is user1 or user2
            chats = Chat.objects.filter(
                models.Q(user1=request.user) | models.Q(user2=request.user)
            ).distinct().order_by('-created_at')

            chat_list = []
            for chat in chats:
                # Determine the other user
                other_user = chat.user2 if chat.user1 == request.user else chat.user1
                # Get the last message (if any)
                last_message = chat.messages.order_by('-created_at').first()
                chat_list.append({
                    "chat_id": str(chat.id),
                    "user": {
                        "user_id": other_user.id,
                        "name": other_user.get_full_name() or other_user.username,
                        "profile_pic_url": other_user.pics.profile_pic_url.url if hasattr(other_user, 'pics') and other_user.pics.profile_pic_url else None
                    },
                    "last_message": {
                        "sender_id": last_message.sender.id,
                        "text": last_message.text,
                        "image_url": last_message.image_url,
                        "created_at": last_message.created_at.timestamp()
                    } if last_message else None,
                    "created_at": chat.created_at.timestamp()
                })

            return Response(
                 chat_list,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error fetching user chats: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import Chat
import logging

logger = logging.getLogger(__name__)

class ChatAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        try:
            recipient_id = request.data.get('recipient_id')
            if not recipient_id:
                return Response(
                    {"error": "Recipient ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                recipient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "Recipient user not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if request.user.id == recipient_id:
                return Response(
                    {"error": "Cannot create a chat with yourself"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check for existing chat
            existing_chat = Chat.objects.filter(
                user1=request.user, user2=recipient
            ).first() or Chat.objects.filter(
                user1=recipient, user2=request.user
            ).first()

            if existing_chat:
                return Response(
                    {"chat_id": str(existing_chat.id)},
                    status=status.HTTP_200_OK
                )

            # Create new chat
            chat = Chat.objects.create(user1=request.user, user2=recipient)
            return Response(
                {"chat_id": str(chat.id)},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error creating chat: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )