import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings

from django_comments import get_model, get_form

from testapp.models import Article, Author

# Shortcut
CT = ContentType.objects.get_for_model


@override_settings(
    PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',),
    ROOT_URLCONF='testapp.urls_default',
)
class CommentTestCase(TestCase):
    """
    Helper base class for comment tests that need data.
    """
    fixtures = ["comment_tests"]

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create(
            username="normaluser",
            first_name="Joe",
            last_name="Normal",
            email="joe.normal@example.com",
        )

    def createSomeComments(self):
        # Two anonymous comments on two different objects
        c1 = get_model().objects.create(
            content_type=CT(Article),
            object_pk="1",
            user_name="Joe Somebody",
            user_email="jsomebody@example.com",
            user_url="http://example.com/~joe/",
            comment="First!",
            site=Site.objects.get_current(),
        )
        c2 = get_model().objects.create(
            content_type=CT(Author),
            object_pk="1",
            user_name="Joe Somebody",
            user_email="jsomebody@example.com",
            user_url="http://example.com/~joe/",
            comment="First here, too!",
            site=Site.objects.get_current(),
        )

        # Two authenticated comments: one on the same Article, and
        # one on a different Author
        user = User.objects.create(
            username="frank_nobody",
            first_name="Frank",
            last_name="Nobody",
            email="fnobody@example.com",
            password="",
            is_staff=False,
            is_active=True,
            is_superuser=False,
        )
        c3 = get_model().objects.create(
            content_type=CT(Article),
            object_pk="1",
            user=user,
            user_url="http://example.com/~frank/",
            comment="Damn, I wanted to be first.",
            site=Site.objects.get_current(),
        )
        c4 = get_model().objects.create(
            content_type=CT(Author),
            object_pk="2",
            user=user,
            user_url="http://example.com/~frank/",
            comment="You get here first, too?",
            site=Site.objects.get_current(),
        )

        return c1, c2, c3, c4

    def getData(self):
        return {
            'name': 'Jim Bob',
            'email': 'jim.bob@example.com',
            'url': '',
            'comment': 'This is my comment',
        }

    def getValidData(self, obj):
        f = get_form()(obj)
        d = self.getData()
        d.update(f.initial)
        return d
