from django.contrib.contenttypes.views import shortcut
from django.urls import path, re_path

from .views.comments import post_comment, comment_done
from .views.moderation import (
    flag, flag_done, delete, delete_done, approve, approve_done,
)


urlpatterns = [
    path('post/', post_comment, name='comments-post-comment'),
    path('posted/', comment_done, name='comments-comment-done'),
    path('flag/<int:comment_id>/', flag, name='comments-flag'),
    path('flagged/', flag_done, name='comments-flag-done'),
    path('delete/<int:comment_id>/', delete, name='comments-delete'),
    path('deleted/', delete_done, name='comments-delete-done'),
    path('approve/<int:comment_id>/', approve, name='comments-approve'),
    path('approved/', approve_done, name='comments-approve-done'),

    re_path(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),
]
