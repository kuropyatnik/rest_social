from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Post (models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(max_length=120)
    content = models.TextField(max_length=800)
    likes = models.ManyToManyField(User, related_name='liked_posts', symmetrical=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']