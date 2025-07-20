from django.db import models
from django.contrib.auth.models import User
import uuid

def generate_uid() -> str:
    return str(uuid.uuid4())

class ChatRoom(models.Model):
    name = models.CharField(max_length=200, default=generate_uid, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    is_ai_chat = models.BooleanField(default=False)
    last_update_at = models.DateTimeField(auto_now=True)

    def all_messages(self, user_id: int, last_id: int = -1) -> list[dict]:
        messages = []
        user = User.objects.filter(id=user_id).first()
        if not user:
            return messages

        if self.messages.exists():
            if last_id < 0:
                last_id = self.messages.last().id
            msg_queryset = self.messages.filter(id__gt=last_id).order_by('-id')[:200]
            new_last_id = msg_queryset[0].id if msg_queryset else last_id

            for msg in msg_queryset:
                sender_details = {
                    "user_id": self.user.id if self.user else None,
                    "name": (self.user.get_full_name() if self.user else "AI Bot"),
                    "profile_pic_url": (self.user.profile_pic_url if self.user and hasattr(self.user, 'profile_pic_url') else None),
                    "is_bot": msg.is_bot
                }
                messages.append({
                    "room_id": self.id,
                    "last_id": new_last_id,
                    "is_me": self.user == user if self.user else False,
                    "user_details": sender_details,
                    "message": {
                        "message_id": msg.id,
                        "text": msg.text,
                        "image_urls": [u.url for u in msg.imageurls.all()],
                        "video_urls": [u.url for u in msg.videourls.all()]
                    }
                })
        return messages

    def __str__(self):
        return f"ChatRoom: {self.name} {'(AI)' if self.is_ai_chat else ''}"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    is_bot = models.BooleanField(default=False)
    text = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "AI Bot" if self.is_bot else "User"
        return f"Message in {self.room.name} by {sender}"

class ChatMessageImageUrl(models.Model):
    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, related_name='imageurls')
    url = models.ImageField(upload_to="uploads", blank=True, null=True)

    def __str__(self):
        return f"Image URL for message {self.message.id}"

class ChatMessageVideoUrl(models.Model):
    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, related_name='videourls')
    url = models.TextField()

    def __str__(self):
        return f"Video URL for message {self.message.id}"
    

# user chat model

from django.db import models
from django.contrib.auth.models import User
import uuid

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chats_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Chat between {self.user1} and {self.user2}"

class ChatHistory(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)  # Text content
    image_url = models.URLField(blank=True, null=True)  # Image URL
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} in chat {self.chat}"

class ChatImage(models.Model):
    file = models.ImageField(upload_to='chat_images/')
    uploader = models.ForeignKey(User, related_name='uploaded_chat_images', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.file.name} by {self.uploader}"