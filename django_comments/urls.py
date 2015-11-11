from django.conf.urls import url
from django.contrib.contenttypes.views import shortcut

from .views.comments import post_comment, comment_done
from .views.moderation import (
    flag, flag_done, delete, delete_done, approve, approve_done,
)


urlpatterns = [
    url(r'^post/$', post_comment, name='comments-post-comment'),
    url(r'^posted/$', comment_done, name='comments-comment-done'),
    url(r'^flag/(\d+)/$', flag, name='comments-flag'),
    url(r'^flagged/$', flag_done, name='comments-flag-done'),
    url(r'^delete/(\d+)/$', delete, name='comments-delete'),
    url(r'^deleted/$', delete_done, name='comments-delete-done'),
    url(r'^approve/(\d+)/$', approve, name='comments-approve'),
    url(r'^approved/$', approve_done, name='comments-approve-done'),

    url(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),
]
