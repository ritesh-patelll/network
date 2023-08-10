from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


from .models import User, Post


@login_required
def edit_post(request, post_id):
    """
    This function allows a user to edit a post. The function first checks if the request 
    method is PUT, otherwise it returns an error. It then queries for the requested post and 
    checks if the post exists and if the logged in user is the owner of the post, otherwise it 
    returns an error. If the 'content' key exists in the request body, it updates the post 
    content and saves the post.
    """
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    post = Post.objects.get(pk=post_id)

    if not post or post.user != request.user:
        return JsonResponse({"error": "Post not found."}, status=404)
        
    data = json.loads(request.body)

    if data.get('content') is not None:
        post.content = data['content']
    post.save()
    return JsonResponse({"message": "Post updated successfully."}, status=201)

@login_required
def like_post(request, post_id):
    """
    This function toggles likes for a post. First, it checks if the post exists, 
    otherwise it returns an error. It then toggles a like on the post from the 
    user making the request, and saves the post. It returns a JsonResponse with 
    the new like count for the post.
    """

    post = Post.objects.filter(pk=post_id).first()
    if not post:
        return JsonResponse({'message': 'Post not found.'}, status=404)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    post.save()

    return JsonResponse({'likes_count': post.likes.count()}, status=201)

def index(request):
    """
    This function handles the index view. If the request is a POST request, and the 
    user is authenticated, it creates a new post with the content from the request.
    If the user is not authenticated, it redirects to the login view.
    """

    if request.method == "POST":
        if request.user.is_authenticated:
            content = request.POST["content"]
            post = Post(user=request.user, content=content)
            post.save()
        else:
            return redirect("login")

    return render(request, "network/index.html")

def all_posts(request):
    """
    This function retrieves all posts and sorts them by timestamp. It implements 
    pagination with 10 posts per page. The function then renders the 'all_posts.html' 
    template with the page object as context.
    """

    posts = Post.objects.all().order_by('-timestamp')
    
    paginator = Paginator(posts, 10)  # Show 10 posts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/all_posts.html", {"page_obj": page_obj})

@login_required
def profile(request, username):
    """
    This function retrieves a user's profile. It counts the followers and followings 
    of the user and retrieves all the user's posts. It implements pagination with 
    10 posts per page. The function then renders the 'profile.html' template with 
    the user's profile, followers and followings count, and posts as context.
    """

    user_profile = User.objects.get(username=username)
    following_count = user_profile.following.count()
    followers_count = user_profile.followers.count()

    posts = user_profile.posts.order_by("-timestamp")

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_profile': user_profile,
        'following_count': following_count,
        'followers_count': followers_count,
        'page_obj': page_obj,
    }

    return render(request, 'network/profile.html', context)

@login_required
def following_posts(request):
    """
    This function retrieves the posts made by the users whom the current user is following. 
    It sorts these posts by timestamp and implements pagination with 10 posts per page. 
    The function then renders the 'following_posts.html' template with the page object as context.
    """

    following_users = request.user.following.all()
    
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following_posts.html", {"page_obj": page_obj})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
