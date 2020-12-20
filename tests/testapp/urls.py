from django.contrib.contenttypes.views import shortcut
from django.urls import path, re_path

from django_comments.feeds import LatestCommentFeed

from custom_comments import views


feeds = {
    'comments': LatestCommentFeed,
}

urlpatterns = [
    path('post/', views.custom_submit_comment),
    path('flag/<int:comment_id>/', views.custom_flag_comment),
    path('delete/<int:comment_id>/', views.custom_delete_comment),
    path('approve/<int:comment_id>/', views.custom_approve_comment),

    re_path(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),

    path('rss/comments/', LatestCommentFeed()),
]
