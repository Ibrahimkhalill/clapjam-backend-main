from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from .chatbot import alcoholbot  # Adjust import based on your app structure
from .models import ChatRoom
from .serializers import ChatRoomSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def alcoholbot_view(request):
    """
    View to handle POST requests for the alcohol bot.
    Requires authentication.
    """
    if request.method == "POST":
        return alcoholbot(request)
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_ai_chat(request):
    """
    View to fetch all AI chat messages for the authenticated user.
    Returns serialized messages with text, image URLs, video URLs, and metadata.
    If no AI chat room exists, returns an empty messages array.
    Requires authentication.
    """
    user = request.user

    # Get AI chat room
    chat_room = ChatRoom.objects.filter(is_ai_chat=True, user=user).first()

    # Serialize the chat room with messages
    serializer = ChatRoomSerializer(chat_room)
    
    return Response(serializer.data)