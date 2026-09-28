from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .models import Post, Like, Comment, Follow, Notification


def home(request):

    posts = Post.objects.all().order_by('-created_at')

    liked_posts = set()

    following_users = set()

    search_query = request.GET.get('q', '').strip()

    if search_query:

        posts = posts.filter(
            Q(content__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    if request.user.is_authenticated:

        liked_posts = set(
            Like.objects.filter(
                user=request.user
            ).values_list(
                'post_id',
                flat=True
            )
        )

        following_users = set(
            Follow.objects.filter(
                follower=request.user
            ).values_list(
                'following_id',
                flat=True
            )
        )

        suggestions = User.objects.exclude(
            id=request.user.id
        ).order_by('username')[:5]

    else:

        suggestions = User.objects.all().order_by('username')[:5]

    return render(
        request,
        'core/home.html',
        {
            'posts': posts,
            'liked_posts': liked_posts,
            'suggestions': suggestions,
            'following_users': following_users,
            'search_query': search_query,
        }
    )


def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password or not confirm_password:

            messages.error(
                request,
                'Please fill in all fields.'
            )

            return redirect('register')

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return redirect('register')

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return redirect('register')

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                'Email is already registered.'
            )

            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            'Account created successfully! You can now log in.'
        )

        return redirect('login')

    return render(
        request,
        'core/register.html'
    )


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect('home')

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

            return redirect('login')

    return render(
        request,
        'core/login.html'
    )


def logout_view(request):

    logout(request)

    return redirect('login')


def create_post(request):

    if not request.user.is_authenticated:

        return redirect('login')

    if request.method == 'POST':

        content = request.POST.get('content')
        image = request.POST.get('image')

        if content:

            Post.objects.create(
                user=request.user,
                content=content,
                image=image or ''
            )

        return redirect('home')

    return redirect('home')


def like_post(request, post_id):
    
    if not request.user.is_authenticated:

        return redirect('login')

    post = get_object_or_404(
        Post,
        id=post_id
    )

    like = Like.objects.filter(
        post=post,
        user=request.user
    ).first()

    if like:

        like.delete()

    else:

        Like.objects.create(
            post=post,
            user=request.user
        )

        if post.user != request.user:

            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                notification_type='like',
                post=post
            )

    return redirect('home')
def create_comment(request, post_id):
    
    if not request.user.is_authenticated:

        return redirect('login')

    post = get_object_or_404(
        Post,
        id=post_id
    )

    if request.method == 'POST':

        content = request.POST.get('content')

        if content:

            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

            if post.user != request.user:

                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='comment',
                    post=post
                )

    return redirect('home')
def follow_user(request, user_id):
    
    if not request.user.is_authenticated:

        return redirect('login')

    target_user = get_object_or_404(
        User,
        id=user_id
    )

    if target_user == request.user:

        return redirect('home')

    follow = Follow.objects.filter(
        follower=request.user,
        following=target_user
    ).first()

    if follow:

        follow.delete()

    else:

        Follow.objects.create(
            follower=request.user,
            following=target_user
        )

        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow'
        )

    return redirect('home')

def profile(request, user_id):

    profile_user = get_object_or_404(
        User,
        id=user_id
    )

    posts = Post.objects.filter(
        user=profile_user
    ).order_by('-created_at')

    is_following = False

    if request.user.is_authenticated:

        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    return render(
        request,
        'core/profile.html',
        {
            'profile_user': profile_user,
            'posts': posts,
            'is_following': is_following,
        }
    )
def liked_posts(request):
    
    if not request.user.is_authenticated:

        return redirect('login')

    posts = Post.objects.filter(
        likes__user=request.user
    ).distinct().order_by('-created_at')

    liked_posts_set = set(
        posts.values_list(
            'id',
            flat=True
        )
    )

    return render(
        request,
        'core/liked_posts.html',
        {
            'posts': posts,
            'liked_posts': liked_posts_set,
        }
    )
def following(request):
    
    if not request.user.is_authenticated:

        return redirect('login')

    following_users = User.objects.filter(
        followers__follower=request.user
    ).order_by('username')

    return render(
        request,
        'core/following.html',
        {
            'following_users': following_users,
        }
    )
def notifications(request):
    
    if not request.user.is_authenticated:

        return redirect('login')

    notification_list = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return render(
        request,
        'core/notifications.html',
        {
            'notifications': notification_list,
        }
    )