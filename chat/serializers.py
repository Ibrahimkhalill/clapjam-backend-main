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
    image_urls = serializers.SerializerMethodField()
    video_urls = serializers.SerializerMethodField()
    sent_at = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = ChatMessage
        fields = ['id', 'is_bot', 'text', 'image_urls', 'video_urls', 'sent_at']

    def get_image_urls(self, obj):
        request = self.context.get('request', None)
        urls = []
        for image in obj.imageurls.all():
            raw_url = image.url.url  # May look like "/media/media/..."
            clean_url = self.clean_media_url(raw_url)
            if request:
                urls.append(request.build_absolute_uri(clean_url))
            else:
                urls.append(clean_url)
        return urls

    def get_video_urls(self, obj):
        request = self.context.get('request', None)
        urls = []
        for video in obj.videourls.all():
            raw_url = video.url.url
            clean_url = self.clean_media_url(raw_url)
            if request:
                urls.append(request.build_absolute_uri(clean_url))
            else:
                urls.append(clean_url)
        return urls

    def clean_media_url(self, url):
        return url.replace('/media/media/', '/media/')


class ChatRoomSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='id', read_only=True)
    room_name = serializers.CharField(source='name', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['room_id', 'room_name', 'user_id', 'messages']