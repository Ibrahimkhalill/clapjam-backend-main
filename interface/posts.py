from django.db.models import QuerySet
from posts import models


class Poster:
    
    def __init__(
        self, user: models.User,
        caption: str | None=None,
        privacy: str='Public',
        poll: dict | None=None,
        event: dict | None=None,
        images: list | None=None,  # Now expects file objects
        videos: list | None=None   # Now expects file objects
    ):
        self.user = user
        self.caption = caption
        self.poll = poll
        self.event = event
        self.privacy = privacy
        self.images = images
        self.videos = videos

        
    def create_metadata(self) -> models.PostMetaData:
        return models.PostMetaData.objects.create(user=self.user, privacy=self.privacy)
    
    def create_text(
        self, metadata: models.PostMetaData) -> models.PostText:
        if self.caption is not None:
            return models.PostText.objects.create(metadata=metadata, content=self.caption)
        
    def create_images(self, metadata: models.PostMetaData) -> None:
        if self.images is not None:
            for image_file in self.images:
                models.PostImageUrl.objects.create(image=metadata, file=image_file)

    def create_videos(self, metadata: models.PostMetaData) -> None:
        if self.videos is not None:
            for video_file in self.videos:
                models.PostVideoUrl.objects.create(image=metadata, file=video_file)
    
    def create_poll(self, metadata: models.PostMetaData) -> models.PostPoll:
        if self.poll is not None:
            poll = models.PostPoll.objects.create(
                metadata=metadata, title=self.poll['title'], poll_type=self.poll['poll_type'])

            for option in self.poll['options']:
                models.PollOption.objects.create(poll=poll, content=option)

            return poll
    
    def create_event(self, metadata: models.PostMetaData) -> models.PostEvent:
        if self.event is not None:
            return models.PostEvent.objects.create(metadata=metadata, **self.event)
    
    def create_post(self) -> models.PostMetaData:
        metadata = self.create_metadata()
        self.create_text(metadata)
        self.create_poll(metadata)
        self.create_event(metadata)
        self.create_images(metadata)  # Handle image file uploads
        self.create_videos(metadata)  # Handle video file uploads
        return metadata


class PostViewer:
    
    def __init__(self, user: models.User) -> None:
        self.user = user
    
    def get_post_ids(self) -> list[int]:
        public_post_ids = [p.id for p in models.PostMetaData.objects.filter(
            privacy=models.PostMetaData.PUBLIC).order_by('-id')]
        print(public_post_ids)
        followed = [f.followed for f in self.user.following.all()]
        followed_users_post_ids = [p.id for p in models.PostMetaData.objects.filter(
            user__in=followed).order_by('-id')]
        print(followed_users_post_ids)
        print(public_post_ids.__len__(), followed_users_post_ids.__len__())
        print(list(set(public_post_ids + followed_users_post_ids)))
        return list(set(public_post_ids + followed_users_post_ids))[::-1]
        
    
    def get_viewable_posts_queryset(self) -> QuerySet:
        return models.PostMetaData.objects.filter(id__in=self.get_post_ids()).order_by('-created_at')