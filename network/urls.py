
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following_posts", views.following_posts, name="following_posts"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("like_post/<int:post_id>", views.like_post, name="like_post"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
