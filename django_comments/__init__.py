from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


DEFAULT_COMMENTS_APP = 'django_comments'

def get_comment_app():
    """
    Get the comment app (i.e. "django_comments") as defined in the settings
    """
    # Make sure the app's in INSTALLED_APPS
    comments_app = get_comment_app_name()
    if comments_app not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("The COMMENTS_APP (%r) "\
                                   "must be in INSTALLED_APPS" % settings.COMMENTS_APP)

    # Try to import the package
    try:
        package = import_module(comments_app)
    except ImportError as e:
        raise ImproperlyConfigured("The COMMENTS_APP setting refers to "\
                                   "a non-existing package. (%s)" % e)

    return package

def get_comment_app_name():
    """
    Returns the name of the comment app (either the setting value, if it
    exists, or the default).
    """
    return getattr(settings, 'COMMENTS_APP', DEFAULT_COMMENTS_APP)

def get_model():
    from django_comments.models import Comment
    """
    Returns the comment model class.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_model"):
        return get_comment_app().get_model()
    else:
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
        return urlresolvers.reverse("django_comments.views.comments.post_comment")

def get_flag_url(comment):
    """
    Get the URL for the "flag this comment" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_flag_url"):
        return get_comment_app().get_flag_url(comment)
    else:
        return urlresolvers.reverse("django_comments.views.moderation.flag",
                                    args=(comment.id,))

def get_delete_url(comment):
    """
    Get the URL for the "delete this comment" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_delete_url"):
        return get_comment_app().get_delete_url(comment)
    else:
        return urlresolvers.reverse("django_comments.views.moderation.delete",
                                    args=(comment.id,))

def get_approve_url(comment):
    """
    Get the URL for the "approve this comment from moderation" view.
    """
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_approve_url"):
        return get_comment_app().get_approve_url(comment)
    else:
        return urlresolvers.reverse("django_comments.views.moderation.approve",
                                    args=(comment.id,))
