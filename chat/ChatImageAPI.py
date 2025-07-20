from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.validators import FileExtensionValidator
import logging
from .models import *
logger = logging.getLogger(__name__)

class ChatImageAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        try:
            images = request.FILES.getlist('images')
            if not images:
                return Response(
                    {"error": "At least one image is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
            max_image_size = 5 * 1024 * 1024  # 5MB
            errors = []
            uploaded_images = []

            for image in images:
                try:
                    image_validator(image)
                    if image.size > max_image_size:
                        errors.append(f"Image file {image.name} exceeds 5MB limit")
                        continue
                    chat_image = ChatImage.objects.create(uploader=request.user, file=image)
                    uploaded_images.append({
                        "url": chat_image.file.url,
                        "filename": image.name
                    })
                except Exception as e:
                    errors.append(f"Invalid image file {image.name}: {str(e)}")

            if errors:
                return Response(
                    {"error": errors if len(errors) > 1 else errors[0]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {"images": uploaded_images},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error uploading chat images: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

