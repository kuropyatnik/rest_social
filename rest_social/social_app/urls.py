from django.urls import path
from .views import registerUserView

urlpatterns = [
    path('register/', registerUserView, name='register'),
]