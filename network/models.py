from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('User', related_name='followers', blank=True)

    def follow(self, user):
        self.following.add(user)

    def unfollow(self, user):
        self.following.remove(user)

    def is_following(self, user):
        if user in self.following.all():
            return True
        return False


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.username,
            'content': self.content,
            'timestamp': self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            'likes': [user.username for user in self.likes.all()],
        }