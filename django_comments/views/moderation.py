from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect

import django_comments
from django_comments import signals
from django_comments.views.utils import next_redirect, confirmation_view


@csrf_protect
@login_required
def flag(request, comment_id, next=None):
    """
    Flags a comment. Confirmation on GET, action on POST.

    Templates: :template:`comments/flag.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    comment = get_object_or_404(django_comments.get_model(),
                                pk=comment_id,
                                site__pk=get_current_site(request).pk)

    # Flag on POST
    if request.method == 'POST':
        perform_flag(request, comment)
        return next_redirect(request, fallback=next or 'comments-flag-done',
                             c=comment.pk)

    # Render a form on GET
    else:
        return render(request, 'comments/flag.html', {'comment': comment, "next": next})


@csrf_protect
@permission_required("django_comments.can_moderate")
def delete(request, comment_id, next=None):
    """
    Deletes a comment. Confirmation on GET, action on POST. Requires the "can
    moderate comments" permission.

    Templates: :template:`comments/delete.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    comment = get_object_or_404(django_comments.get_model(),
                                pk=comment_id,
                                site__pk=get_current_site(request).pk)

    # Delete on POST
    if request.method == 'POST':
        # Flag the comment as deleted instead of actually deleting it.
        perform_delete(request, comment)
        return next_redirect(request, fallback=next or 'comments-delete-done',
                             c=comment.pk)

    # Render a form on GET
    else:
        return render(request, 'comments/delete.html', {'comment': comment, "next": next})


@csrf_protect
@permission_required("django_comments.can_moderate")
def approve(request, comment_id, next=None):
    """
    Approve a comment (that is, mark it as public and non-removed). Confirmation
    on GET, action on POST. Requires the "can moderate comments" permission.

    Templates: :template:`comments/approve.html`,
    Context:
        comment
            the `comments.comment` object for approval
    """
    comment = get_object_or_404(django_comments.get_model(),
                                pk=comment_id,
                                site__pk=get_current_site(request).pk)

    # Delete on POST
    if request.method == 'POST':
        # Flag the comment as approved.
        perform_approve(request, comment)
        return next_redirect(request, fallback=next or 'comments-approve-done',
                             c=comment.pk)

    # Render a form on GET
    else:
        return render(request, 'comments/approve.html', {'comment': comment, "next": next})


# The following functions actually perform the various flag/aprove/delete
# actions. They've been broken out into separate functions to that they
# may be called from admin actions.

def perform_flag(request, comment):
    """
    Actually perform the flagging of a comment from a request.
    """
    flag, created = django_comments.models.CommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=django_comments.models.CommentFlag.SUGGEST_REMOVAL
    )
    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_delete(request, comment):
    flag, created = django_comments.models.CommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=django_comments.models.CommentFlag.MODERATOR_DELETION
    )
    comment.is_removed = True
    comment.save()
    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_approve(request, comment):
    flag, created = django_comments.models.CommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=django_comments.models.CommentFlag.MODERATOR_APPROVAL,
    )

    comment.is_removed = False
    comment.is_public = True
    comment.save()

    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )

# Confirmation views.

flag_done = confirmation_view(
    template="comments/flagged.html",
    doc='Displays a "comment was flagged" success page.'
)
delete_done = confirmation_view(
    template="comments/deleted.html",
    doc='Displays a "comment was deleted" success page.'
)
approve_done = confirmation_view(
    template="comments/approved.html",
    doc='Displays a "comment was approved" success page.'
)
