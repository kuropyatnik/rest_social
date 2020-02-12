from django.urls import path
from .views import register_user_view, login_view

urlpatterns = [
    path('register/', register_user_view, name='register'),
    path('login/', login_view, name='login'),
]