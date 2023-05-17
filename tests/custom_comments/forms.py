from django import forms

from django_comments.forms import CommentForm


class CustomCommentForm(CommentForm):
    file = forms.FileField()

    def get_comment_create_data(self, site_id=None):
        data = super().get_comment_create_data(site_id=site_id)
        data["file"] = self.cleaned_data["file"]
        return data
