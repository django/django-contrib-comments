from django.core.exceptions import ImproperlyConfigured
from django.test.utils import modify_settings, override_settings

import django_comments
from django_comments.models import Comment
from django_comments.forms import CommentForm

from . import CommentTestCase


class CommentAppAPITests(CommentTestCase):
    """Tests for the "comment app" API"""

    def testGetCommentApp(self):
        self.assertEqual(django_comments.get_comment_app(), django_comments)

    @modify_settings(INSTALLED_APPS={'remove': 'django_comments'})
    def testGetMissingCommentApp(self):
        msg = "The COMMENTS_APP ('django_comments') must be in INSTALLED_APPS"
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
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
