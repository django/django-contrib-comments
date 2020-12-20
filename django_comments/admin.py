from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _, ngettext

from django_comments import get_model
from django_comments.views.moderation import perform_flag, perform_approve, perform_delete


class UsernameSearch:
    """The User object may not be auth.User, so we need to provide
    a mechanism for issuing the equivalent of a .filter(user__username=...)
    search in CommentAdmin.
    """

    def __str__(self):
        return 'user__%s' % get_user_model().USERNAME_FIELD


class CommentsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {'fields': ('content_type', 'object_pk', 'site')}
        ),
        (
            _('Content'),
            {'fields': ('user', 'user_name', 'user_email', 'user_url', 'comment')}
        ),
        (
            _('Metadata'),
            {'fields': ('submit_date', 'ip_address', 'is_public', 'is_removed')}
        ),
    )

    list_display = ('name', 'content_type', 'object_pk', 'ip_address', 'submit_date', 'is_public', 'is_removed')
    list_filter = ('submit_date', 'site', 'is_public', 'is_removed')
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    raw_id_fields = ('user',)
    search_fields = ('comment', UsernameSearch(), 'user_name', 'user_email', 'user_url', 'ip_address')
    actions = ["flag_comments", "approve_comments", "remove_comments"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Only superusers should be able to delete the comments from the DB.
        if not request.user.is_superuser and 'delete_selected' in actions:
            actions.pop('delete_selected')
        if not request.user.has_perm('django_comments.can_moderate'):
            if 'approve_comments' in actions:
                actions.pop('approve_comments')
            if 'remove_comments' in actions:
                actions.pop('remove_comments')
        return actions

    def flag_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_flag,
                        lambda n: ngettext('flagged', 'flagged', n))

    flag_comments.short_description = _("Flag selected comments")

    def approve_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_approve,
                        lambda n: ngettext('approved', 'approved', n))

    approve_comments.short_description = _("Approve selected comments")

    def remove_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_delete,
                        lambda n: ngettext('removed', 'removed', n))

    remove_comments.short_description = _("Remove selected comments")

    def _bulk_flag(self, request, queryset, action, done_message):
        """
        Flag, approve, or remove some comments from an admin action. Actually
        calls the `action` argument to perform the heavy lifting.
        """
        n_comments = 0
        for comment in queryset:
            action(request, comment)
            n_comments += 1

        msg = ngettext('%(count)s comment was successfully %(action)s.',
                        '%(count)s comments were successfully %(action)s.',
                        n_comments)
        self.message_user(request, msg % {'count': n_comments, 'action': done_message(n_comments)})


# Only register the default admin if the model is the built-in comment model
# (this won't be true if there's a custom comment app).
Klass = get_model()
if Klass._meta.app_label == "django_comments":
    admin.site.register(Klass, CommentsAdmin)
