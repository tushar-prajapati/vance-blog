from django.urls import path
from .views import (
    PostListView, 
    PostDetailView, 
    like_post_api, 
    add_comment_api, 
    subscribe_newsletter_api
)

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('newsletter/subscribe/', subscribe_newsletter_api, name='newsletter_subscribe_api'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/like/', like_post_api, name='post_like_api'),
    path('<slug:slug>/comment/', add_comment_api, name='post_comment_api'),
]
