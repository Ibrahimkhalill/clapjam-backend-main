from django.urls import path
from .views import *
urlpatterns = [
    # Cocktail URLs
    path('cocktails/list/', cocktail_list, name='cocktail_list'),
    path('cocktails/<int:pk>/', cocktail_detail, name='cocktail_detail'),
    path('cocktails/create/', cocktail_create, name='cocktail_create'),
    path('cocktails/<int:pk>/update/', cocktail_update, name='cocktail_update'),
    path('cocktails/<int:pk>/delete/', cocktail_delete, name='cocktail_delete'),
    
    
    # BookMark URLs
    path('bookmarks/', bookmark_list, name='bookmark_list'),
    path('bookmarks/<int:pk>/', bookmark_detail, name='bookmark_detail'),
    path('bookmarks/create/', bookmark_create, name='bookmark_create'),
    path('bookmarks/<int:pk>/update/', bookmark_update, name='bookmark_update'),
    path('bookmarks/<int:pk>/delete/', bookmark_delete, name='bookmark_delete'),

    #
    path('cocktails/ai/genarate/receipe/', user_genarate_receipe_ai)
]