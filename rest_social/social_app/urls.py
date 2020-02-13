from django.urls import path
from django.conf.urls import url
from .views import register_user_view, login_view, add_post_view, get_all_posts_view, get_post_view

urlpatterns = [
    path('register/', register_user_view, name='register'),
    path('login/', login_view, name='login'),
    path('add-post/', add_post_view, name='add-post'),
    path('posts/', get_all_posts_view, name='posts'),
    # url(r'^get-post/(?P<pk>\d+)$', get_post_view, name='get-post'),
    path('post/<int:pk>/', get_post_view, name='post')
]
