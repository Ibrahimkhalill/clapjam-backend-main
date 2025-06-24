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

    

class UserPostAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
     
    def get(self, request: Request) -> Response:
        # post privacy based view will be implemented
        return Response(dict(
            posts = [p.details() for p in models.PostMetaData.objects.filter(
                user=request.user).order_by('-id')]
        ))
    
    def post(self, request: Request) -> Response:

        print(request.data)
        poster = Poster(user=request.user, **request.data)
        metadata = poster.create_post()
        return Response(metadata.details(), status=status.HTTP_200_OK)
        # except Exception as e: 
        #     # error in dev; MUST be changed in prod
        #     return Response(dict(errors=[str(e)]), status=status.HTTP_400_BAD_REQUEST)


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
    

class PostAddCommentAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request, metadata_id: int) -> Response: 
        metadata = models.PostMetaData.objects.filter(id=metadata_id).first()
        if metadata is not None:
            content = request.data.get('text')
            comment = models.PostComment.objects.create(
                metadata=metadata, user=request.user, content=content)
            return Response(dict(comment=comment.details), status=status.HTTP_200_OK)
        return Response(dict(errors=[msg.INVALID_ID]), status=status.HTTP_404_NOT_FOUND)


class PostAddReplyAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request, comment_id: int) -> Response: 
        comment = models.PostComment.objects.filter(id=comment_id).first()
        if comment is not None:
            content = request.data.get('text')
            reply = models.PostCommentReply.objects.create(
                comment=comment, user=request.user, content=content)
            return Response(dict(reply=reply.details), status=status.HTTP_200_OK)
        return Response(dict(errors=[msg.INVALID_ID]), status=status.HTTP_404_NOT_FOUND)
            

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
