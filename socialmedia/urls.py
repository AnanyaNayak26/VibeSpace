from django.contrib import admin
from django.urls import path

from core.views import (
    home,
    register,
    login_view,
    logout_view,
    create_post,
    like_post,
    create_comment,
    follow_user,
    profile,
    liked_posts,
    following,
    notifications,
)


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        home,
        name='home'
    ),

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    path(
        'create-post/',
        create_post,
        name='create_post'
    ),

    path(
        'like/<int:post_id>/',
        like_post,
        name='like_post'
    ),

    path(
        'comment/<int:post_id>/',
        create_comment,
        name='create_comment'
    ),

    path(
        'follow/<int:user_id>/',
        follow_user,
        name='follow_user'
    ),

    path(
        'profile/<int:user_id>/',
        profile,
        name='profile'
    ),

    path(
        'liked-posts/',
        liked_posts,
        name='liked_posts'
    ),

    path(
        'following/',
        following,
        name='following'
    ),

    path(
        'notifications/',
        notifications,
        name='notifications'
    ),

]