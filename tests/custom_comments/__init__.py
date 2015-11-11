from django.core import urlresolvers

from . import views
from .forms import CustomCommentForm


def get_model():
    from .models import CustomComment
    return CustomComment


def get_form():
    return CustomCommentForm


def get_form_target():
    return urlresolvers.reverse(views.custom_submit_comment)


def get_flag_url(c):
    return urlresolvers.reverse(views.custom_flag_comment, args=(c.id,))


def get_delete_url(c):
    return urlresolvers.reverse(views.custom_delete_comment, args=(c.id,))


def get_approve_url(c):
    return urlresolvers.reverse(views.custom_approve_comment, args=(c.id,))
