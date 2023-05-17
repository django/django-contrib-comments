from django.db import models

from django_comments.models import Comment


class CustomComment(Comment):
    file = models.FileField()
