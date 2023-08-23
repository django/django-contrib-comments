from django.urls import reverse

from . import views


def get_model():
    from .models import CustomComment
    return CustomComment


def get_form():
    from .forms import CustomCommentForm
    return CustomCommentForm


def get_form_target():
    return reverse(views.custom_submit_comment)


def get_flag_url(c):
    return reverse(views.custom_flag_comment, args=(c.id,))


def get_delete_url(c):
    return reverse(views.custom_delete_comment, args=(c.id,))


def get_approve_url(c):
    return reverse(views.custom_approve_comment, args=(c.id,))
