from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(ChatRoom)
admin.site.register(ChatMessageImageUrl)

# user chat
admin.site.register(Chat)
admin.site.register(ChatHistory)
admin.site.register(ChatImage)