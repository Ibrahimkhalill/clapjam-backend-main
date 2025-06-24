import os
import io
import uuid
import base64
import json
from PIL import Image
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
from dotenv import load_dotenv
from .models import ChatRoom, ChatMessage, ChatMessageImageUrl

# Load .env variables
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Allowed alcohol-related keywords
ALCOHOL_KEYWORDS = [
    "alcohol",
    "drink",
    "wine",
    "vodka",
    "whiskey",
    "rum",
    "beer",
    "gin",
    "tequila",
    "brandy",
    "cocktail",
    "liquor",
    "spirits",
    "bottle",
    "bourbon",
]

# Helper: Check if a message is alcohol-related based on keywords
def is_alcohol_related(message):
    if not message:
        return False
    return any(keyword in message.lower() for keyword in ALCOHOL_KEYWORDS)

# Helper: Check if conversation context is alcohol-related
def is_conversation_alcohol_related(chat_room):
    last_messages = ChatMessage.objects.filter(room=chat_room).order_by('-sent_at')[:5]
    for msg in last_messages:
        if is_alcohol_related(msg.text):
            return True
    return False

# Helper: Generate image-based alcohol information
def generate_image_analysis(image_bytes):
    prompt = (
        "You're an expert alcohol identification assistant. Given this image of an alcohol bottle, "
        "return ONLY these 12 fields in this exact format using emojis. Write 'Not specified' if unknown.\n\n"
        "🔍 Identified alcohol:\n"
        "🌍 Origin:\n"
        "🍸 Alcohol Content:\n"
        "🌾 Main Ingredient:\n"
        "💅 Tasting Notes:\n"
        "🔹 Similar kind of alcohol (at least 3):\n"
        "🔗 Want to mix a cocktail? Try a recipe:\n"
        "✨ AI Bot Interactive Features:\n"
        "📊 Confidence Level:\n"
        "🏷 Brand Logo & History:\n"
        "🎥 YouTube Link:\n"
        "📦 Buy Online Link:\n"
        "🔄 Ask Again:"
    )

    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert alcohol assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                        },
                    ],
                },
            ],
            temperature=0.3,
            max_tokens=700,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Helper: Generate response based on text and conversation history
def generate_text_response(message, chat_room):
    if not (is_alcohol_related(message) or is_conversation_alcohol_related(chat_room)):
        return "❌ This assistant only supports alcohol-related questions."

    try:
        last_messages = ChatMessage.objects.filter(room=chat_room).order_by('-sent_at')[:5]
        last_messages = list(reversed(last_messages))

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert alcohol assistant. Respond to the user's latest message "
                    "while considering the conversation history. Keep responses alcohol-related, "
                    "informative, and concise."
                )
            }
        ]

        for msg in last_messages:
            role = "assistant" if msg.is_bot else "user"
            content = msg.text
            if msg.imageurls.exists():
                image_urls = [str(img.url) for img in msg.imageurls.all()]
                if image_urls:
                    content += f"\n[Image URLs: {', '.join(image_urls)}]"
            messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error processing text: {str(e)}"

# Main Django function to handle alcohol bot requests
def alcoholbot(request):
    """
    Django function to handle alcohol bot requests for authenticated users only.
    Saves user messages and bot replies to a single AI chat room per user, associating the user
    with the room on first chat. Images are saved permanently to media/uploads/.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Authentication required to use the alcohol bot."},
            status=401
        )

    try:
        response_data = {}
        user = request.user

        message_text = None
        image_file = None
        image_base64 = None
        room_id = None

        is_json = request.content_type.startswith('application/json')

        if is_json:
            try:
                json_data = json.loads(request.body.decode('utf-8'))
                message_text = json_data.get('text') or json_data.get('message')
                image_base64 = json_data.get('image_base64')
                room_id = json_data.get('room_id')
            except json.JSONDecodeError:
                return JsonResponse(
                    {"success": False, "error": "Invalid JSON format."}, status=400
                )
        else:
            message_text = request.POST.get('message') or request.POST.get('text')
            image_file = request.FILES.get('image')
            room_id = request.POST.get('room_id')

        if room_id:
            chat_room = ChatRoom.objects.filter(id=room_id, is_ai_chat=True, user=user).first()
            if not chat_room:
                return JsonResponse(
                    {"success": False, "error": "Invalid AI chat room ID or access denied."},
                    status=400
                )
        else:
            chat_room = ChatRoom.objects.filter(is_ai_chat=True, user=user).first()
            if not chat_room:
                chat_room = ChatRoom.objects.create(
                    name=str(uuid.uuid4()),
                    is_ai_chat=True,
                    user=user
                )

        upload_folder = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        user_message_id = None
        image_path = None

        if message_text or image_file or image_base64:
            user_message = ChatMessage.objects.create(
                room=chat_room,
                is_bot=False,
                text=message_text or ""
            )
            user_message_id = user_message.id

        if image_file and image_file.name:
            filename = f"{uuid.uuid4()}_{image_file.name}"
            path = os.path.join(upload_folder, filename)
            
            with open(path, "wb") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            try:
                image = Image.open(path).convert("RGB")
                byte_stream = io.BytesIO()
                image.save(byte_stream, format="JPEG")
                image_bytes = byte_stream.getvalue()

                image_response = generate_image_analysis(image_bytes)
                response_data["image_response"] = image_response
                # Save relative path for ImageField
                image_path = os.path.join("uploads", filename).replace(os.sep, "/")
                ChatMessageImageUrl.objects.create(message=user_message, url=image_path)
            except Exception as e:
                user_message.delete()
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Image processing failed: {str(e)}",
                    },
                    status=400,
                )

        elif image_base64:
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            try:
                image_bytes = base64.b64decode(image_base64)
                image_response = generate_image_analysis(image_bytes)
                response_data["image_response"] = image_response
                filename = f"{uuid.uuid4()}_base64.jpg"
                path = os.path.join(upload_folder, filename)
                with open(path, "wb") as f:
                    f.write(image_bytes)
                # Save relative path for ImageField
                image_path = os.path.join("uploads", filename).replace(os.sep, "/")
                ChatMessageImageUrl.objects.create(message=user_message, url=image_path)
            except Exception as e:
                user_message.delete()
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Base64 image processing failed: {str(e)}",
                    },
                    status=400,
                )

        if message_text:
            text_response = generate_text_response(message_text, chat_room)
            response_data["text_response"] = text_response

        if not response_data and not user_message_id:
            return JsonResponse(
                {"success": False, "error": "No valid input provided."}, status=400
            )

        bot_message_id = None
        if response_data.get("text_response") or response_data.get("image_response"):
            bot_message = ChatMessage.objects.create(
                room=chat_room,
                is_bot=True,
                text=response_data.get("text_response", "") or response_data.get("image_response", "")
            )
            bot_message_id = bot_message.id
            if image_path:
                ChatMessageImageUrl.objects.create(message=bot_message, url=image_path)

        response_data["success"] = True
        response_data["room_id"] = chat_room.id
        response_data["user_message_id"] = user_message_id
        response_data["bot_message_id"] = bot_message_id

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"success": False, "error": f"Server error: {str(e)}"}, status=500)