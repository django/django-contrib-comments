from __future__ import absolute_import

import unittest

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
from django.utils import six

import django_comments
from django_comments.models import Comment
from django_comments.forms import CommentForm

from . import CommentTestCase


class CommentAppAPITests(CommentTestCase):
    """Tests for the "comment app" API"""

    def testGetCommentApp(self):
        self.assertEqual(django_comments.get_comment_app(), django_comments)

    @unittest.skipIf(django.VERSION >= (1, 7), "Missing apps raise ImportError with django 1.7")
    @override_settings(
        COMMENTS_APP='missing_app',
        INSTALLED_APPS=list(settings.INSTALLED_APPS) + ['missing_app'],
    )
    def testGetMissingCommentApp(self):
        with six.assertRaisesRegex(self, ImproperlyConfigured, 'missing_app'):
            django_comments.get_comment_app()

    def testGetForm(self):
        self.assertEqual(django_comments.get_form(), CommentForm)

    def testGetFormTarget(self):
        self.assertEqual(django_comments.get_form_target(), "/post/")

    def testGetFlagURL(self):
        c = Comment(id=12345)
        self.assertEqual(django_comments.get_flag_url(c), "/flag/12345/")

    def getGetDeleteURL(self):
        c = Comment(id=12345)
        self.assertEqual(django_comments.get_delete_url(c), "/delete/12345/")

    def getGetApproveURL(self):
        c = Comment(id=12345)
        self.assertEqual(django_comments.get_approve_url(c), "/approve/12345/")


@override_settings(
    COMMENTS_APP='custom_comments', ROOT_URLCONF='testapp.urls',
)
class CustomCommentTest(CommentTestCase):

    def testGetCommentApp(self):
        import custom_comments
        self.assertEqual(django_comments.get_comment_app(), custom_comments)

    def testGetModel(self):
        from custom_comments.models import CustomComment
        self.assertEqual(django_comments.get_model(), CustomComment)

    def testGetForm(self):
        from custom_comments.forms import CustomCommentForm
        self.assertEqual(django_comments.get_form(), CustomCommentForm)

    def testGetFormTarget(self):
        self.assertEqual(django_comments.get_form_target(), "/post/")

    def testGetFlagURL(self):
        c = Comment(id=12345)
        self.assertEqual(django_comments.get_flag_url(c), "/flag/12345/")

    def getGetDeleteURL(self):
        c = Comment(id=12345)
        self.assertEqual(django_comments.get_delete_url(c), "/delete/12345/")

    def getGetApproveURL(self):
        c = Comment(id=12345)
        self.assertEqual(django_comments.get_approve_url(c), "/approve/12345/")
