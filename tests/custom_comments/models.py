from django.db.models import FileField
from django_comments.abstracts import CommentAbstractModel


class CustomComment(CommentAbstractModel):
    file = FileField()
