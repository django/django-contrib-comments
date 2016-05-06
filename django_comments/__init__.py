from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured


DEFAULT_COMMENTS_APP = 'django_comments'


def get_comment_app():
    """
    Get the comment app (i.e. "django_comments") as defined in the settings
    """
    # Make sure the app's in INSTALLED_APPS
    comments_app = get_comment_app_name()
    if not apps.is_installed(comments_app):
        raise ImproperlyConfigured(
            "The COMMENTS_APP (%r) must be in INSTALLED_APPS" % comments_app
        )

    # Try to import the package
    try:
        package = import_module(comments_app)
    except ImportError as e:
        raise ImproperlyConfigured(
            "The COMMENTS_APP setting refers to a non-existing package. (%s)" % e
        )

    return package


def get_comment_app_name():
    """
    Returns the name of the comment app (either the setting value, if it
    exists, or the default).
    """
    return getattr(settings, 'COMMENTS_APP', DEFAULT_COMMENTS_APP)


def get_model():
    """
    Returns the comment model class.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_model"):
        return get_comment_app().get_model()
    else:
        from django_comments.models import Comment
        return Comment


def get_form():
    from django_comments.forms import CommentForm
    """
    Returns the comment ModelForm class.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_form"):
        return get_comment_app().get_form()
    else:
        return CommentForm


def get_form_target():
    """
    Returns the target URL for the comment form submission view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_form_target"):
        return get_comment_app().get_form_target()
    else:
        return urlresolvers.reverse("comments-post-comment")


def get_flag_url(comment):
    """
    Get the URL for the "flag this comment" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_flag_url"):
        return get_comment_app().get_flag_url(comment)
    else:
        return urlresolvers.reverse("comments-flag", args=(comment.id,))


def get_delete_url(comment):
    """
    Get the URL for the "delete this comment" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_delete_url"):
        return get_comment_app().get_delete_url(comment)
    else:
        return urlresolvers.reverse("comments-delete", args=(comment.id,))


def get_approve_url(comment):
    """
    Get the URL for the "approve this comment from moderation" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_approve_url"):
        return get_comment_app().get_approve_url(comment)
    else:
        return urlresolvers.reverse("comments-approve", args=(comment.id,))
