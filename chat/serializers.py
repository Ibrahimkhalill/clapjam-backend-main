from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatMessageImageUrl, ChatMessageVideoUrl

class ChatMessageImageUrlSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(use_url=True)

    class Meta:
        model = ChatMessageImageUrl
        fields = ['url']

class ChatMessageVideoUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageVideoUrl
        fields = ['url']

class ChatMessageSerializer(serializers.ModelSerializer):
    image_urls = ChatMessageImageUrlSerializer(many=True, read_only=True, source='imageurls')
    video_urls = ChatMessageVideoUrlSerializer(many=True, read_only=True, source='videourls')
    sent_at = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = ChatMessage
        fields = ['id', 'is_bot', 'text', 'image_urls', 'video_urls', 'sent_at']
       

class ChatRoomSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='id', read_only=True)
    room_name = serializers.CharField(source='name', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['room_id', 'room_name', 'user_id', 'messages']