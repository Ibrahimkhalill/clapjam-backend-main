import time
from django.db import models
from django.contrib.auth.models import User
from profiles.models import City, Follow
from utils import keygen as kg, subroutines as sr


def generate_uid() -> str:
    return kg.KeyGen().timestamped_alphanumeric_id()


class PostMetaData(models.Model):
    PUBLIC = 'Public'; FOLLOWERS = 'Followers'; ONLY_ME = 'Only me'
    PRIVACY_CHOICES = ((PUBLIC, PUBLIC), (FOLLOWERS, FOLLOWERS), (ONLY_ME, ONLY_ME))
    
    uid = models.CharField(
        max_length=50, unique=True, default=generate_uid)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_metadata')
    privacy = models.CharField(
        max_length=10, choices=PRIVACY_CHOICES, default=PUBLIC)
    created_at = models.BigIntegerField(null=True, blank=True)
    updated_at = models.BigIntegerField(null=True, blank=True)
    
    @property
    def viewers(self) -> models.QuerySet:
        return {
            self.PUBLIC : User.objects.all(),
            self.FOLLOWERS: Follow.get_followers(self.user),
            self.ONLY_ME : User.objects.filter(id=self.user.id)
        }[self.privacy]
    
    def is_valid_viewer(self, user_id: int) -> bool:
        return self.viewers.filter(id=user_id).exists()
    
    def is_follower(self, user: User) -> bool:
        return self.user.followers.filter(follower=user).exists()
    
    @property
    def total_comments(self) -> int:
        total = self.comments.count() if hasattr(self, 'comments') else 0
        if total > 0:
            for comment in self.comments.all():
                total += comment.replies.count()
        return total
    
    @property
    def total_likes(self) -> int:
        return self.likes.count() if hasattr(self, 'likes') else 0
    
    @property
    def all_likes(self) -> dict:
        _likes = [l for l in self.likes.all()] if hasattr(self, 'likes') else list()
        return dict(
            total = self.total_likes,
            likers=[dict(
                user_id = like.user.id,
                name = like.user.get_full_name(),
                profile_pic_url = like.user.pics.profile_pic_url
            ) for like in _likes]
        )
    
    @property
    def all_comments(self) -> dict:
        comment_list = [comment.details for comment in self.comments.all()] if hasattr(self, 'comments') else list()
        return dict(
            total = self.total_comments,
            comment_list = comment_list
        )
    
    def details(self, viewer=None) -> dict:
        has_text = hasattr(self, 'text')
        has_poll = hasattr(self, 'poll')
        has_event = hasattr(self, 'event')
        has_image = self.imageurls.exists()
        has_video = self.videourls.exists() 

        # Author info
        author = dict(
            user_id=self.user.id,
            name=self.user.get_full_name(),
            profile_pic_url=self.user.pics.profile_pic_url,
        )

        # Default like status
        viewer_liked = False

        # Check viewer context
        if viewer is not None:
            author['is_following'] = self.is_follower(viewer)
            author['viewer_is_author'] = self.user == viewer
            viewer_liked = self.likes.filter(user=viewer).exists()  # ✅ Check if viewer liked
       

        metadata = dict(
            id=self.id,
            uid=self.uid,
            post_privacy=self.privacy,
            total_likes=self.total_likes,
            total_comments=self.total_comments,
            created_at=self.created_at,
            updated_at=self.updated_at,
            has_text=has_text,
            has_image=has_image,
            has_video=has_video,
            has_poll=has_poll,
            has_event=has_event,
            viewer_liked=viewer_liked  # ✅ Include in metadata
        )

        caption = self.text.content if has_text else None
        images = [u.url for u in self.imageurls.all()]
        videos = [u.url for u in self.videourls.all()]
        poll = self.poll.analysis if has_poll else None
        event = sr.get_clean_dict(self.event) if has_event else None

        return dict(
            metadata=metadata,
            author=author,
            caption=caption,
            images=images,
            videos=videos,
            poll=poll,
            event=event
        )


    
    def save(self, *args, **kwargs) -> None:
        ts = sr.current_timestamp()
        if self._state.adding:
            self.created_at = ts
        self.updated_at = ts
        # if self.privacy not in self.PRIVACY_CHOICES:
        #     raise ValueError('Invalid privacy choice.')
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Post Meta Data'

    
class PostText(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=generate_uid)
    metadata = models.OneToOneField(
        PostMetaData, on_delete=models.CASCADE, related_name='text')
    content = models.TextField(default='')


class PostImageUrl(models.Model):
    image = models.ForeignKey(
        PostMetaData, on_delete=models.CASCADE, related_name='imageurls')
    url = models.TextField()


class PostVideoUrl(models.Model):
    image = models.ForeignKey(
        PostMetaData, on_delete=models.CASCADE, related_name='videourls')
    url = models.TextField()
    

class PostEvent(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=generate_uid)
    metadata = models.OneToOneField(
        PostMetaData, on_delete=models.CASCADE, related_name='event')
    title = models.TextField(default='Epic event!')
    date = models.BigIntegerField(default=-1)
    time = models.CharField(max_length=20, default='', blank=True, null=True)
    country = models.CharField(max_length=100, default='', blank=True, null=True)
    city = models.CharField(max_length=100, default='', blank=True, null=True)
    place_id = models.CharField(max_length=100, default='', blank=True, null=True)
    longitude = models.CharField(max_length=100, default='', blank=True, null=True)
    latitude = models.CharField(max_length=100, default='', blank=True, null=True)
    post_code = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(default='Epic event!', blank=True, null=True)
    
    def __str__(self):
        return f'Event: PostMetadata {self.metadata.id}'
    
    def save(self, *args, **kwargs) -> None:
        if self.date == -1:
            self.date = sr.current_timestamp()
        
        super().save(*args, **kwargs)
    

class PostPoll(models.Model):
    Single = 'Single'; Multuple = 'Multiple'
    POLL_TYPE_CHOICES = ((Single, Single), (Multuple, Multuple))
    
    uid = models.CharField(
        max_length=50, unique=True, default=generate_uid)
    metadata = models.OneToOneField(
        PostMetaData, on_delete=models.CASCADE, related_name='poll')
    title = models.TextField(default='')
    poll_type = models.CharField(
        max_length=15, choices=POLL_TYPE_CHOICES, default=Single)
    
    @property
    def total_vote(self) -> int:
        return sum([opt.total_vote for opt in self.options.all()])
    
    @property
    def analysis(self) -> list[dict]:
        poll_analysis = list()
        total_poll_vote = self.total_vote
        for opt in self.options.all():
            frac = opt.total_vote / total_poll_vote if total_poll_vote > 0 else 0
            perc = round(frac * 100, 2)
            poll_analysis.append(dict(
                option_id = opt.id,
                content = opt.content,
                vote = opt.total_vote,
                perc = perc
            ))    
        return dict(
            id = self.id,
            uid = self.uid,
            title = self.title,
            poll_type = self.poll_type,
            options = sorted(poll_analysis, key=lambda x: x['perc'], reverse=True)
        )


class PollOption(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=generate_uid)
    poll = models.ForeignKey(
        PostPoll, on_delete=models.CASCADE, related_name='options')
    content = models.TextField()
    
    @property
    def total_vote(self) -> int:
        return self.votes.count()


class PollVote(models.Model):
    poll_option = models.ForeignKey(
        PollOption, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)


class PostLike(models.Model):
    metadata = models.ForeignKey(
        PostMetaData, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('metadata', 'user'),
                name='unique_liker'
            )
        ]


class PostComment(models.Model):
    metadata = models.ForeignKey(
        PostMetaData, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default='')
    
    @property
    def reply_list(self) -> list:
        return [reply.details for reply in self.replies.all()] if hasattr(self, 'replies') else list()
    
    @property
    def details(self) -> dict:
        pics=[pic.url for pic in self.pics.all()] if hasattr(self, 'pics') else list()
        return dict(
            comment_id=self.id,
            user = dict(
                user_id = self.user.id,
                name = self.user.get_full_name(),
                profile_pic_url = self.user.pics.profile_pic_url
            ),
            text = self.content,
            pics = pics,
            replies = self.reply_list
        )


class PostCommentPic(models.Model):
    comment = models.ForeignKey(
        PostComment, on_delete=models.CASCADE, related_name='pics')
    url = models.TextField(default='')

    
class PostCommentReply(models.Model): 
    comment = models.ForeignKey(
        PostComment, on_delete=models.CASCADE, related_name='replies', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content = models.TextField(default='')
    
    @property
    def details(self) -> dict:
        pics=[pic.url for pic in self.pics.all()] if hasattr(self, 'pics') else list()
        return dict(
            reply_id = self.id,
            user = dict(
                user_id = self.user.id,
                name = self.user.get_full_name(),
                profile_pic_url = self.user.pics.profile_pic_url
            ),
            text = self.content,
            pics = pics
        )


class PostCommentReplyPic(models.Model): 
    reply = models.ForeignKey(
        PostCommentReply, on_delete=models.CASCADE, related_name='pics')
    url = models.TextField(default='')
