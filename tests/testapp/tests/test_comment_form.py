from __future__ import absolute_import

import time

from django.conf import settings
from django.contrib.sites.models import Site

from django_comments.forms import CommentForm
from django_comments.models import Comment

from . import CommentTestCase
from testapp.models import Article


class CommentFormTests(CommentTestCase):

    def setUp(self):
        super(CommentFormTests, self).setUp()
        self.site_2 = Site.objects.create(id=settings.SITE_ID + 1,
            domain="testserver", name="testserver")

    def testInit(self):
        f = CommentForm(Article.objects.get(pk=1))
        self.assertEqual(f.initial['content_type'], str(Article._meta))
        self.assertEqual(f.initial['object_pk'], "1")
        self.assertNotEqual(f.initial['security_hash'], None)
        self.assertNotEqual(f.initial['timestamp'], None)

    def testValidPost(self):
        a = Article.objects.get(pk=1)
        f = CommentForm(a, data=self.getValidData(a))
        self.assertTrue(f.is_valid(), f.errors)
        return f

    def tamperWithForm(self, **kwargs):
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)
        d.update(kwargs)
        f = CommentForm(Article.objects.get(pk=1), data=d)
        self.assertFalse(f.is_valid())
        return f

    def testHoneypotTampering(self):
        self.tamperWithForm(honeypot="I am a robot")

    def testTimestampTampering(self):
        self.tamperWithForm(timestamp=str(time.time() - 28800))

    def testSecurityHashTampering(self):
        self.tamperWithForm(security_hash="Nobody expects the Spanish Inquisition!")

    def testContentTypeTampering(self):
        self.tamperWithForm(content_type="auth.user")

    def testObjectPKTampering(self):
        self.tamperWithForm(object_pk="3")

    def testSecurityErrors(self):
        f = self.tamperWithForm(honeypot="I am a robot")
        self.assertTrue("honeypot" in f.security_errors())

    def testGetCommentObject(self):
        f = self.testValidPost()
        c = f.get_comment_object()
        self.assertTrue(isinstance(c, Comment))
        self.assertEqual(c.content_object, Article.objects.get(pk=1))
        self.assertEqual(c.comment, "This is my comment")
        c.save()
        self.assertEqual(Comment.objects.count(), 1)

        # Create a comment for the second site. We only test for site_id, not
        # what has already been tested above.
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)
        d["comment"] = "testGetCommentObject with a site"
        f = CommentForm(Article.objects.get(pk=1), data=d)
        c = f.get_comment_object(site_id=self.site_2.id)
        self.assertEqual(c.site_id, self.site_2.id)

    def testProfanities(self):
        """Test COMMENTS_ALLOW_PROFANITIES and PROFANITIES_LIST settings"""
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)

        # Save settings in case other tests need 'em
        saved = getattr(settings, 'PROFANITIES_LIST', []), getattr(settings, 'COMMENTS_ALLOW_PROFANITIES', False)

        # Don't wanna swear in the unit tests if we don't have to...
        settings.PROFANITIES_LIST = ["rooster"]

        # Try with COMMENTS_ALLOW_PROFANITIES off
        settings.COMMENTS_ALLOW_PROFANITIES = False
        f = CommentForm(a, data=dict(d, comment="What a rooster!"))
        self.assertFalse(f.is_valid())

        # Now with COMMENTS_ALLOW_PROFANITIES on
        settings.COMMENTS_ALLOW_PROFANITIES = True
        f = CommentForm(a, data=dict(d, comment="What a rooster!"))
        self.assertTrue(f.is_valid())

        # Restore settings
        settings.PROFANITIES_LIST, settings.COMMENTS_ALLOW_PROFANITIES = saved
