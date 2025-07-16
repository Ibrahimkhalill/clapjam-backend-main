from django.urls import path
from . import views


urlpatterns = [
    # auth
    path('user/register', views.RegisterAPI.as_view()),
    path('user/login', views.LoginAPI.as_view()),
    path('user/token-lifetime', views.TokenLifetimeAPI.as_view()),
    path('user/refresh-token', views.RefreshTokenAPI.as_view()),
    path('user/profile/', views.ProfileAPI.as_view()),
    path('user/verify-email', views.EmailVerificationAPI.as_view()),
    path('user/verify-otp', views.OTPVerificationAPI.as_view()),
    path('user/change-password', views.PwdChangeAPI.as_view()),
    path('user/request-otp', views.OTPRequestAPI.as_view()),
    
    # standalone
    path('countries', views.CountriesAPI.as_view()),
    path('cities', views.citiesAPI.as_view()),
    
    # user posts
    path('user/posts', views.UserPostAPI.as_view()),
    path('user/posts/<int:metadata_id>', views.UserPostAPI.as_view()),
    path('user/post/click-like/<int:metadata_id>', views.PostClickLikeAPI.as_view()),

    path('user/post/add-comment/<int:metadata_id>', views.PostAddCommentAPI.as_view()),
    path('user/post/comment/<int:comment_id>', views.PostAddCommentAPI.as_view(), name='post-comment-update-delete'),

    path('user/post/add-reply/<int:comment_id>', views.PostAddReplyAPI.as_view()),
    path('user/post/reply/<int:reply_id>', views.PostAddReplyAPI.as_view(), name='post-reply-get-update-delete'),
    path('user/post/comment/get-reply/<int:comment_id>', views.PostCommentsRepliesAPI.as_view(), name='post-reply-get'),
    
    # posts
    path('posts/feed', views.PostFeedAPI.as_view()),
    path('posts/likes/<metadata_id>', views.PostLikesAPI.as_view()),
    path('posts/comments/<metadata_id>', views.PostCommentsAPI.as_view()),
]
