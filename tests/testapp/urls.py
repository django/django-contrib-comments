from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.contenttypes.views import shortcut

from django_comments.feeds import LatestCommentFeed

from custom_comments import views


feeds = {
    'comments': LatestCommentFeed,
}

urlpatterns = [
    url(r'^post/$', views.custom_submit_comment),
    url(r'^flag/(\d+)/$', views.custom_flag_comment),
    url(r'^delete/(\d+)/$', views.custom_delete_comment),
    url(r'^approve/(\d+)/$', views.custom_approve_comment),

    url(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),

    url(r'^rss/comments/$', LatestCommentFeed()),
]
