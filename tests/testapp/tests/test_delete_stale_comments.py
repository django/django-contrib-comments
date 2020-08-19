from django.core.management import call_command

from django_comments.models import Comment

from . import CommentTestCase
from testapp.models import Article


class CommentManagerTests(CommentTestCase):

    def testDoesNotRemoveWhenNoStaleComments(self):
        self.createSomeComments()
        initial_count = Comment.objects.count()

        call_command("delete_stale_comments", "--yes", verbosity=0)

        self.assertEqual(initial_count, Comment.objects.count())

    def testRemovesWhenParentObjectsAreMissing(self):
        self.createSomeComments()
        initial_count = Comment.objects.count()
        article_comments_count = Comment.objects.for_model(Article).count()
        self.assertGreater(article_comments_count, 0)

        # removing articles will not remove associated comments
        Article.objects.all().delete()
        self.assertEqual(initial_count, Comment.objects.count())

        call_command("delete_stale_comments", "--yes", verbosity=0)

        self.assertEqual(0, Comment.objects.for_model(Article).count())
        self.assertEqual(initial_count - article_comments_count, Comment.objects.count())
