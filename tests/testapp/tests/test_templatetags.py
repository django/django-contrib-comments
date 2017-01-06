from __future__ import absolute_import

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template import Template, Context
from django.test.client import RequestFactory
from django.test.utils import override_settings

from django_comments.forms import CommentForm
from django_comments.models import Comment

from testapp.models import Article, Author
from . import CommentTestCase


class CommentTemplateTagTests(CommentTestCase):

    def setUp(self):
        super(CommentTemplateTagTests, self).setUp()
        self.site_2 = Site.objects.create(id=settings.SITE_ID + 1,
            domain="testserver", name="testserver")

    def render(self, t, **c):
        ctx = Context(c)
        out = Template(t).render(ctx)
        return ctx, out

    def testCommentFormTarget(self):
        ctx, out = self.render("{% load comments %}{% comment_form_target %}")
        self.assertEqual(out, "/post/")

    def testGetCommentForm(self, tag=None):
        t = "{% load comments %}" + (tag or "{% get_comment_form for testapp.article a.id as form %}")
        ctx, out = self.render(t, a=Article.objects.get(pk=1))
        self.assertEqual(out, "")
        self.assertTrue(isinstance(ctx["form"], CommentForm))

    def testGetCommentFormFromLiteral(self):
        self.testGetCommentForm("{% get_comment_form for testapp.article 1 as form %}")

    def testGetCommentFormFromObject(self):
        self.testGetCommentForm("{% get_comment_form for a as form %}")

    def testWhitespaceInGetCommentFormTag(self):
        self.testGetCommentForm("{% load comment_testtags %}{% get_comment_form for a|noop:'x y' as form %}")

    def testRenderCommentForm(self, tag=None):
        t = "{% load comments %}" + (tag or "{% render_comment_form for testapp.article a.id %}")
        ctx, out = self.render(t, a=Article.objects.get(pk=1))
        self.assertTrue(out.strip().startswith("<form action="))
        self.assertTrue(out.strip().endswith("</form>"))

    def testRenderCommentFormFromLiteral(self):
        self.testRenderCommentForm("{% render_comment_form for testapp.article 1 %}")

    def testRenderCommentFormFromObject(self):
        self.testRenderCommentForm("{% render_comment_form for a %}")

    def testWhitespaceInRenderCommentFormTag(self):
        self.testRenderCommentForm("{% load comment_testtags %}{% render_comment_form for a|noop:'x y' %}")

    def testRenderCommentFormFromObjectWithQueryCount(self):
        with self.assertNumQueries(1):
            self.testRenderCommentFormFromObject()

    def verifyGetCommentCount(self, tag=None):
        t = "{% load comments %}" + (tag or "{% get_comment_count for testapp.article a.id as cc %}") + "{{ cc }}"
        ctx, out = self.render(t, a=Article.objects.get(pk=1))
        self.assertEqual(out, "2")

    def testGetCommentCount(self):
        self.createSomeComments()
        self.verifyGetCommentCount("{% get_comment_count for testapp.article a.id as cc %}")

    def testGetCommentCountFromLiteral(self):
        self.createSomeComments()
        self.verifyGetCommentCount("{% get_comment_count for testapp.article 1 as cc %}")

    def testGetCommentCountFromObject(self):
        self.createSomeComments()
        self.verifyGetCommentCount("{% get_comment_count for a as cc %}")

    def testWhitespaceInGetCommentCountTag(self):
        self.createSomeComments()
        self.verifyGetCommentCount("{% load comment_testtags %}{% get_comment_count for a|noop:'x y' as cc %}")

    def verifyGetCommentList(self, tag=None):
        c1, c2, c3, c4 = Comment.objects.all()[:4]
        t = "{% load comments %}" + (tag or "{% get_comment_list for testapp.author a.id as cl %}")
        ctx, out = self.render(t, a=Author.objects.get(pk=1))
        self.assertEqual(out, "")
        self.assertEqual(list(ctx["cl"]), [c2])

    def testGetCommentList(self):
        self.createSomeComments()
        self.verifyGetCommentList("{% get_comment_list for testapp.author a.id as cl %}")

    def testGetCommentListFromLiteral(self):
        self.createSomeComments()
        self.verifyGetCommentList("{% get_comment_list for testapp.author 1 as cl %}")

    def testGetCommentListFromObject(self):
        self.createSomeComments()
        self.verifyGetCommentList("{% get_comment_list for a as cl %}")

    def testGetCommentListUsingRequest(self, tag=None):
        # A request lookup should return site_2
        with override_settings(SITE_ID=self.site_2.id):
            c1, c2, c3, c4 = self.createSomeComments()

        # Effectively unset SITE_ID which forces a site lookup from the
        # request. Create a new comment for the second site.
        with override_settings(SITE_ID=None):
            t = "{% load comments %}" + (tag or "{% get_comment_list for testapp.author a.id as cl %}")
            request = RequestFactory().get("/")
            ctx, out = self.render(t, a=Author.objects.get(pk=1), request=request)
            self.assertEqual(list(ctx["cl"]), [c2])

    def testWhitespaceInGetCommentListTag(self):
        self.createSomeComments()
        self.verifyGetCommentList("{% load comment_testtags %}{% get_comment_list for a|noop:'x y' as cl %}")

    def testGetCommentPermalink(self):
        c1, c2, c3, c4 = self.createSomeComments()
        t = "{% load comments %}{% get_comment_list for testapp.author author.id as cl %}"
        t += "{% get_comment_permalink cl.0 %}"
        ct = ContentType.objects.get_for_model(Author)
        author = Author.objects.get(pk=1)
        ctx, out = self.render(t, author=author)
        self.assertEqual(out, "/cr/%s/%s/#c%s" % (ct.id, author.id, c2.id))

    def testGetCommentPermalinkFormatted(self):
        c1, c2, c3, c4 = self.createSomeComments()
        t = "{% load comments %}{% get_comment_list for testapp.author author.id as cl %}"
        t += "{% get_comment_permalink cl.0 '#c%(id)s-by-%(user_name)s' %}"
        ct = ContentType.objects.get_for_model(Author)
        author = Author.objects.get(pk=1)
        ctx, out = self.render(t, author=author)
        self.assertEqual(out, "/cr/%s/%s/#c%s-by-Joe Somebody" % (ct.id, author.id, c2.id))

    def testWhitespaceInGetCommentPermalinkTag(self):
        c1, c2, c3, c4 = self.createSomeComments()
        t = "{% load comments comment_testtags %}{% get_comment_list for testapp.author author.id as cl %}"
        t += "{% get_comment_permalink cl.0|noop:'x y' %}"
        ct = ContentType.objects.get_for_model(Author)
        author = Author.objects.get(pk=1)
        ctx, out = self.render(t, author=author)
        self.assertEqual(out, "/cr/%s/%s/#c%s" % (ct.id, author.id, c2.id))

    def testRenderCommentList(self, tag=None):
        t = "{% load comments %}" + (tag or "{% render_comment_list for testapp.article a.id %}")
        ctx, out = self.render(t, a=Article.objects.get(pk=1))
        self.assertTrue(out.strip().startswith("<dl id=\"comments\">"))
        self.assertTrue(out.strip().endswith("</dl>"))

    def testRenderCommentListFromLiteral(self):
        self.testRenderCommentList("{% render_comment_list for testapp.article 1 %}")

    def testRenderCommentListFromObject(self):
        self.testRenderCommentList("{% render_comment_list for a %}")

    def testWhitespaceInRenderCommentListTag(self):
        self.testRenderCommentList("{% load comment_testtags %}{% render_comment_list for a|noop:'x y' %}")

    def testNumberQueries(self):
        """
        Ensure that the template tags use cached content types to reduce the
        number of DB queries.
        Refs #16042.
        """

        self.createSomeComments()

        # {% render_comment_list %} -----------------

        # Clear CT cache
        ContentType.objects.clear_cache()
        with self.assertNumQueries(3):
            self.testRenderCommentListFromObject()

        # CT's should be cached
        with self.assertNumQueries(2):
            self.testRenderCommentListFromObject()

        # {% get_comment_list %} --------------------

        ContentType.objects.clear_cache()
        with self.assertNumQueries(4):
            self.verifyGetCommentList()

        with self.assertNumQueries(3):
            self.verifyGetCommentList()

        # {% render_comment_form %} -----------------

        ContentType.objects.clear_cache()
        with self.assertNumQueries(3):
            self.testRenderCommentForm()

        with self.assertNumQueries(2):
            self.testRenderCommentForm()

        # {% get_comment_form %} --------------------

        ContentType.objects.clear_cache()
        with self.assertNumQueries(3):
            self.testGetCommentForm()

        with self.assertNumQueries(2):
            self.testGetCommentForm()

        # {% get_comment_count %} -------------------

        ContentType.objects.clear_cache()
        with self.assertNumQueries(3):
            self.verifyGetCommentCount()

        with self.assertNumQueries(2):
            self.verifyGetCommentCount()
