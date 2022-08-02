import time
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test.utils import override_settings
from freezegun import freeze_time
from testapp.models import Article

from django_comments.forms import CommentForm
from django_comments.models import Comment

from . import CommentTestCase

CT = ContentType.objects.get_for_model

class CommentFormTests(CommentTestCase):

    def setUp(self):
        super().setUp()
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

    @freeze_time("2012-01-14 13:21:34")
    def test_get_comment_create_data_uuid(self):
        """
        The get_comment_create_data() method returns
        uuid field as  object_pk if overriden by settings
        """
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)
        d["comment"] = "testGetCommentObject with a site"
        f = CommentForm(Article.objects.get(pk=1), data=d)
        self.assertTrue(f.is_valid())
        with override_settings(
            COMMENTS_ID_OVERRIDES={
                "testapp.Article": "uuid",
            }
        ):
            c = f.get_comment_create_data(site_id=self.site_2.id)
            self.assertDictEqual(
                c,
                {
                    "comment": "testGetCommentObject with a site",
                    "content_type": CT(Article),
                    "is_public": True,
                    "is_removed": False,
                    "object_pk": "336384ea-b04f-4a3a-a06a-1f25a8048f8f",  # uuid is returned
                    "site_id": 2,
                    "submit_date": datetime(2012, 1, 14, 13, 21, 34),
                    "user_email": "jim.bob@example.com",
                    "user_name": "Jim Bob",
                    "user_url": "",
                },
            )
        c = f.get_comment_create_data(site_id=self.site_2.id)
        self.assertDictEqual(
            c,
            {
                "comment": "testGetCommentObject with a site",
                "content_type": CT(Article),
                "is_public": True,
                "is_removed": False,
                "object_pk": "1",  # pk is returned as object_pk
                "site_id": 2,
                "submit_date": datetime(2012, 1, 14, 13, 21, 34),
                "user_email": "jim.bob@example.com",
                "user_name": "Jim Bob",
                "user_url": "",
            },
        )

    @freeze_time("2012-01-14 13:21:34")
    def test_generate_security_data_uuid(self):
        """
        The generate_security_data() method returns
        uuid field as  object_pk if overriden by settings
        """
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)
        d["comment"] = "testGetCommentObject with a site"
        f = CommentForm(Article.objects.get(pk=1), data=d)
        self.assertTrue(f.is_valid())
        with override_settings(
            COMMENTS_ID_OVERRIDES={
                "testapp.Article": "uuid",
            }
        ):
            c = f.generate_security_data()
            self.assertDictEqual(
                c,
                {
                    "content_type": "testapp.article",
                    "object_pk": "336384ea-b04f-4a3a-a06a-1f25a8048f8f",
                    "security_hash": "b89ebc7c1c6ed757991fa06027405aecdf8d51f1",
                    "timestamp": "1326547294",
                },
            )
        c = f.generate_security_data()
        self.assertDictEqual(
            c,
            {
                "content_type": "testapp.article",
                "object_pk": "1",
                "security_hash": "2f4a55f47e58b22791d4d26f3b1a2e594302fb61",
                "timestamp": "1326547294",
            },
        )

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
