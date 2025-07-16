from .libs import *
from posts import models
from interface.posts import Poster, PostViewer
from .. import messages as msg
from rest_framework.pagination import PageNumberPagination


class PostPaginator(PageNumberPagination):
    page_size = 20  
    page_size_query_param = 'size'  
    max_page_size = 100  

    def get_paginated_response(self, data: dict) -> Response:
        return Response(data)


class PostFeedAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]  # Optional: enforce login

    def get(self, request: Request) -> Response:
        viewer = PostViewer(request.user)
        queryset = viewer.get_viewable_posts_queryset()
        paginator = PostPaginator()
        posts: list[models.PostMetaData] = paginator.paginate_queryset(
            queryset=queryset, request=request)
        return paginator.get_paginated_response(
            data=[p.details(viewer=request.user) for p in posts]
        )

    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
import uuid
import logging

logger = logging.getLogger(__name__)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.validators import FileExtensionValidator
import logging
import json

logger = logging.getLogger(__name__)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.validators import FileExtensionValidator
import logging
import json

logger = logging.getLogger(__name__)

class UserPostAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            posts = models.PostMetaData.objects.filter(user=request.user).order_by('-id')
            return Response(
                dict(posts=[p.details(viewer=request.user) for p in posts]),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error fetching user posts: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request: Request) -> Response:
        try:
            print("data", request.data)  # Debugging
            caption = request.data.get('caption')
            privacy = request.data.get('privacy', 'Public')
            poll = request.data.get('poll')
            event = request.data.get('event')
            images = request.FILES.getlist('images')  # Optional
            videos = request.FILES.getlist('videos')  # Optional

            # Parse poll JSON string if provided
            if poll is not None:
                try:
                    if isinstance(poll, str):
                        poll = json.loads(poll)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Poll must be valid JSON"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Parse event JSON string if provided
            if event is not None:
                try:
                    if isinstance(event, str):
                        event = json.loads(event)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Event must be valid JSON"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Validate privacy
            if privacy not in [choice[0] for choice in models.PostMetaData.PRIVACY_CHOICES]:
                return Response(
                    {"error": "Invalid privacy value"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate poll structure
            errors = []
            if poll is not None:
                if not isinstance(poll, dict):
                    errors.append("Poll must be a dictionary")
                else:
                    required_keys = ['title', 'options', 'poll_type']
                    if not all(key in poll for key in required_keys):
                        errors.append("Poll must contain title, options, and poll_type")
                    if not isinstance(poll['options'], list) or not poll['options']:
                        errors.append("Poll options must be a non-empty list")
                    if poll['poll_type'] not in ['Single', 'Multiple']:
                        errors.append("Poll type must be 'Single' or 'Multiple'")

            # Validate event structure
            if event is not None:
                if not isinstance(event, dict):
                    errors.append("Event must be a dictionary")
                else:
                    required_keys = ['country', 'title', 'date', 'time', 'city', 'post_code', 'place_id', 'latitude', 'longitude', 'description']
                    if not all(key in event for key in required_keys):
                        errors.append("Event must contain country, title, date, time, city, post_code, place_id, latitude, longitude, description")

           

            # Ensure at least one content type (images are optional)
            if not (caption or images or videos or poll or event):
                errors.append("At least one of caption, images, videos, poll, or event is required")

            # Return all validation errors if any
            if errors:
                return Response(
                    {"error": errors if len(errors) > 1 else errors[0]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create Poster instance
            poster = Poster(
                user=request.user,
                caption=caption,
                privacy=privacy,
                poll=poll,
                event=event,
                images=images if images else None,
                videos=videos if videos else None
            )

            # Create post and return details
            metadata = poster.create_post()
            return Response(metadata.details(viewer=request.user), status=status.HTTP_200_OK)

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return Response(
                {"error": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request: Request, metadata_id: int) -> Response:
        try:
            post = models.PostMetaData.objects.filter(id=metadata_id, user=request.user).first()
            if not post:
                return Response(
                    {"error": "Post not found or you are not the owner"},
                    status=status.HTTP_404_NOT_FOUND
                )

            caption = request.data.get('caption')
            privacy = request.data.get('privacy')
            poll = request.data.get('poll')
            event = request.data.get('event')
            images = request.FILES.getlist('images')
            videos = request.FILES.getlist('videos')

            # Parse poll JSON string if provided
            if poll is not None:
                try:
                    if isinstance(poll, str):
                        poll = json.loads(poll)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Poll must be valid JSON"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Parse event JSON string if provided
            if event is not None:
                try:
                    if isinstance(event, str):
                        event = json.loads(event)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Event must be valid JSON"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Validate privacy if provided
            errors = []
            if privacy and privacy not in [choice[0] for choice in models.PostMetaData.PRIVACY_CHOICES]:
                errors.append("Invalid privacy value")

            # Validate poll structure
            if poll is not None:
                if not isinstance(poll, dict):
                    errors.append("Poll must be a dictionary")
                else:
                    required_keys = ['title', 'options', 'poll_type']
                    if not all(key in poll for key in required_keys):
                        errors.append("Poll must contain title, options, and poll_type")
                    if not isinstance(poll['options'], list) or not poll['options']:
                        errors.append("Poll options must be a non-empty list")
                    if poll['poll_type'] not in ['Single', 'Multiple']:
                        errors.append("Poll type must be 'Single' or 'Multiple'")

            # Validate event structure
            if event is not None:
                if not isinstance(event, dict):
                    errors.append("Event must be a dictionary")
                else:
                    required_keys = ['country', 'title', 'date', 'time', 'city', 'post_code', 'place_id', 'latitude', 'longitude', 'description']
                    if not all(key in event for key in required_keys):
                        errors.append("Event must contain country, title, date, time, city, post_code, place_id, latitude, longitude, description")

            # Validate files (if provided)
            image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
            video_validator = FileExtensionValidator(allowed_extensions=['mp4', 'avi'])
            max_image_size = 5 * 1024 * 1024
            max_video_size = 10 * 1024 * 1024
            for image in images:
                try:
                    image_validator(image)
                    if image.size > max_image_size:
                        errors.append(f"Image file {image.name} exceeds 5MB limit")
                except Exception as e:
                    errors.append(f"Invalid image file {image.name}: {str(e)}")
            for video in videos:
                try:
                    video_validator(video)
                    if video.size > max_video_size:
                        errors.append(f"Video file {video.name} exceeds 10MB limit")
                except Exception as e:
                    errors.append(f"Invalid video file {video.name}: {str(e)}")

            # Ensure at least one content type remains
            if not (
                (hasattr(post, 'text') and (post.text.content or caption is not None)) or
                post.imageurls.exists() or images or
                post.videourls.exists() or videos or
                hasattr(post, 'poll') or poll or
                hasattr(post, 'event') or event
            ):
                errors.append("Post must have at least one of caption, images, videos, poll, or event")

            # Return all validation errors if any
            if errors:
                return Response(
                    {"error": errors if len(errors) > 1 else errors[0]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update fields if provided
            if privacy:
                post.privacy = privacy
                post.save()

            if caption is not None:
                if hasattr(post, 'text'):
                    post.text.content = caption
                    post.text.save()
                else:
                    models.PostText.objects.create(metadata=post, content=caption)

            if poll is not None:
                if hasattr(post, 'poll'):
                    post.poll.delete()
                if poll:
                    new_poll = models.PostPoll.objects.create(
                        metadata=post, title=poll['title'], poll_type=poll['poll_type']
                    )
                    for option in poll['options']:
                        models.PollOption.objects.create(poll=new_poll, content=option)

            if event is not None:
                if hasattr(post, 'event'):
                    post.event.delete()
                if event:
                    models.PostEvent.objects.create(metadata=post, **event)

            if images:
                post.imageurls.all().delete()
                for image in images:
                    models.PostImageUrl.objects.create(image=post, file=image)

            if videos:
                post.videourls.all().delete()
                for video in videos:
                    models.PostVideoUrl.objects.create(image=post, file=video)

            return Response(post.details(viewer=request.user), status=status.HTTP_200_OK)

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return Response(
                {"error": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating post: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request: Request, metadata_id: int) -> Response:
        try:
            post = models.PostMetaData.objects.filter(id=metadata_id, user=request.user).first()
            if not post:
                return Response(
                    {"error": "Post not found or you are not the owner"},
                    status=status.HTTP_404_NOT_FOUND
                )
            post.delete()
            return Response(
                dict(message="Post deleted successfully"),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error deleting post: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PostClickLikeAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request, metadata_id: int) -> Response:
        metadata = models.PostMetaData.objects.filter(id=metadata_id).first()
        if metadata is not None:
            like, created = models.PostLike.objects.get_or_create(
                metadata=metadata, user=request.user)
            if created:
                # send notification
                pass
            else: like.delete()
            return Response(
                dict(message=msg.SUCCESS, likes=like.metadata.all_likes), status=status.HTTP_200_OK)
        return Response(dict(errors=[msg.INVALID_ID]), status=status.HTTP_404_NOT_FOUND)
    

class PostAddCommentAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, metadata_id: int) -> Response:
        try:
            # Fetch the post
            metadata = models.PostMetaData.objects.filter(id=metadata_id).first()
            if not metadata:
                return Response(
                    dict(errors=["Post not found"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extract data
            content = request.data.get('text', '')
            pics = request.FILES.getlist('pics')  # Handles single or multiple images

            # Validate files
            image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
            max_image_size = 5 * 1024 * 1024  # 5MB
            for pic in pics:
                image_validator(pic)
                if pic.size > max_image_size:
                    return Response(
                        dict(errors=[f"Image file {pic.name} exceeds 5MB limit"]),
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Ensure at least one content type
            if not (content or pics):
                return Response(
                    dict(errors=["At least one of text or images is required"]),
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create comment
            comment = models.PostComment.objects.create(
                metadata=metadata,
                user=request.user,
                content=content
            )

            # Create comment images
            for pic in pics:
                models.PostCommentPic.objects.create(comment=comment, file=pic)

            return Response(
                dict(comment.details),
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return Response(
                dict(errors=[str(ve)]),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request: Request, comment_id: int) -> Response:
        try:
            # Fetch the comment
            comment = models.PostComment.objects.filter(id=comment_id, user=request.user).first()
            if not comment:
                return Response(
                    dict(errors=["Comment not found or you are not the owner"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extract data
            content = request.data.get('text')
            pics = request.FILES.getlist('pics')  # Handles single or multiple images

            # Validate files
            image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
            max_image_size = 5 * 1024 * 1024  # 5MB
            for pic in pics:
                image_validator(pic)
                if pic.size > max_image_size:
                    return Response(
                        dict(errors=[f"Image file {pic.name} exceeds 5MB limit"]),
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Update content if provided
            if content is not None:  # Allow empty string to clear content
                comment.content = content
                comment.save()

            # Update images if provided (replace existing)
            if pics:
                comment.pics.all().delete()  # Clear existing images
                for pic in pics:
                    models.PostCommentPic.objects.create(comment=comment, file=pic)

            # Ensure at least one content type remains
            if not (comment.content or comment.pics.exists()):
                return Response(
                    dict(errors=["Comment must have at least one of text or images"]),
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                dict(comment.details),
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return Response(
                dict(errors=[str(ve)]),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating comment: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request: Request, comment_id: int) -> Response:
        try:
            # Fetch the comment
            comment = models.PostComment.objects.filter(id=comment_id, user=request.user).first()
            if not comment:
                return Response(
                    dict(errors=["Comment not found or you are not the owner"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Delete the comment
            comment.delete()
            return Response(
                dict(message="Comment deleted successfully"),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class PostCommentsRepliesAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, comment_id: int) -> Response:
        try:
            # Fetch the comment
            comment = models.PostComment.objects.filter(id=comment_id).first()
            if not comment:
                return Response(
                    dict(errors=["Comment not found"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get all replies for the comment
            replies = models.PostCommentReply.objects.filter(comment=comment).order_by('id')
            return Response(
                dict(replies=[reply.details for reply in replies]),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error retrieving replies: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        


class PostAddReplyAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, comment_id: int) -> Response:
        try:
            # Fetch the comment
            comment = models.PostComment.objects.filter(id=comment_id).first()
            if not comment:
                return Response(
                    dict(errors=["Comment not found"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extract data
            content = request.data.get('text', '')
            pics = request.FILES.getlist('pics')  # Handles single or multiple images

            # Validate files
            image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
            max_image_size = 5 * 1024 * 1024  # 5MB
            for pic in pics:
                image_validator(pic)
                if pic.size > max_image_size:
                    return Response(
                        dict(errors=[f"Image file {pic.name} exceeds 5MB limit"]),
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Ensure at least one content type
            if not (content or pics):
                return Response(
                    dict(errors=["At least one of text or images is required"]),
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create reply
            reply = models.PostCommentReply.objects.create(
                comment=comment,
                user=request.user,
                content=content
            )

            # Create reply images
            for pic in pics:
                models.PostCommentReplyPic.objects.create(reply=reply, file=pic)

            return Response(
                dict(reply=reply.details),
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return Response(
                dict(errors=[str(ve)]),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating reply: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request: Request, reply_id: int) -> Response:
        try:
            # Fetch the reply
            reply = models.PostCommentReply.objects.filter(id=reply_id).first()
            if not reply:
                return Response(
                    dict(errors=["Reply not found"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                dict(reply=reply.details),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error retrieving reply: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request: Request, reply_id: int) -> Response:
        try:
            # Fetch the reply
            reply = models.PostCommentReply.objects.filter(id=reply_id, user=request.user).first()
            if not reply:
                return Response(
                    dict(errors=["Reply not found or you are not the owner"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extract data
            content = request.data.get('text')
            pics = request.FILES.getlist('pics')  # Handles single or multiple images

            # Validate files
            image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
            max_image_size = 5 * 1024 * 1024  # 5MB
            for pic in pics:
                image_validator(pic)
                if pic.size > max_image_size:
                    return Response(
                        dict(errors=[f"Image file {pic.name} exceeds 5MB limit"]),
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Update content if provided
            if content is not None:  # Allow empty string to clear content
                reply.content = content
                reply.save()

            # Update images if provided (replace existing)
            if pics:
                reply.pics.all().delete()  # Clear existing images
                for pic in pics:
                    models.PostCommentReplyPic.objects.create(reply=reply, file=pic)

            # Ensure at least one content type remains
            if not (reply.content or reply.pics.exists()):
                return Response(
                    dict(errors=["Reply must have at least one of text or images"]),
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                dict(reply=reply.details),
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return Response(
                dict(errors=[str(ve)]),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating reply: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request: Request, reply_id: int) -> Response:
        try:
            # Fetch the reply
            reply = models.PostCommentReply.objects.filter(id=reply_id, user=request.user).first()
            if not reply:
                return Response(
                    dict(errors=["Reply not found or you are not the owner"]),
                    status=status.HTTP_404_NOT_FOUND
                )

            # Delete the reply
            reply.delete()
            return Response(
                dict(message="Reply deleted successfully"),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error deleting reply: {str(e)}")
            return Response(
                dict(errors=[str(e)]),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class PostLikesAPI(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request, metadata_id: int) -> Response:
        metadata = models.PostMetaData.objects.filter(id=metadata_id).first()
        if metadata is not None:
            return Response(metadata.all_likes, status=status.HTTP_200_OK)  
        return Response(dict(errors=[msg.INVALID_ID]), status=status.HTTP_404_NOT_FOUND)


class PostCommentsAPI(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request, metadata_id: int) -> Response:
        metadata = models.PostMetaData.objects.filter(id=metadata_id).first()
        if metadata is not None:
            return Response(metadata.all_comments, status=status.HTTP_200_OK)  
        return Response(dict(errors=[msg.INVALID_ID]), status=status.HTTP_404_NOT_FOUND)
