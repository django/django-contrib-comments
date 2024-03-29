from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test.utils import override_settings
from django.utils import translation

from django_comments import signals
from django_comments.models import Comment, CommentFlag

from . import CommentTestCase


class FlagViewTests(CommentTestCase):

    def testFlagGet(self):
        """GET the flag view: render a confirmation page."""
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.force_login(self.user)
        response = self.client.get("/flag/%d/" % pk)
        self.assertTemplateUsed(response, "comments/flag.html")

    def testFlagPost(self):
        """POST the flag view: actually flag the view (nice for XHR)"""
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.force_login(self.user)
        response = self.client.post("/flag/%d/" % pk)
        self.assertRedirects(response, "/flagged/?c=%d" % pk)
        c = Comment.objects.get(pk=pk)
        self.assertEqual(c.flags.filter(flag=CommentFlag.SUGGEST_REMOVAL).count(), 1)
        return c

    def testFlagPostNext(self):
        """
        POST the flag view, explicitly providing a next url.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.force_login(self.user)
        response = self.client.post("/flag/%d/" % pk, {'next': "/go/here/"})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)

    def testFlagPostUnsafeNext(self):
        """
        POSTing to the flag view with an unsafe next url will ignore the
        provided url when redirecting.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        self.client.force_login(self.user)
        response = self.client.post("/flag/%d/" % pk,
            {'next': "http://elsewhere/bad"})
        self.assertRedirects(response, "/flagged/?c=%d" % pk)

    def testFlagPostTwice(self):
        """Users don't get to flag comments more than once."""
        c = self.testFlagPost()
        self.client.post("/flag/%d/" % c.pk)
        self.client.post("/flag/%d/" % c.pk)
        self.assertEqual(c.flags.filter(flag=CommentFlag.SUGGEST_REMOVAL).count(), 1)

    def testFlagAnon(self):
        """GET/POST the flag view while not logged in: redirect to log in."""
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/flag/%d/" % pk)
        self.assertRedirects(response,
            "/accounts/login/?next=/flag/%d/" % pk,
            fetch_redirect_response=False)
        response = self.client.post("/flag/%d/" % pk)
        self.assertRedirects(response,
            "/accounts/login/?next=/flag/%d/" % pk,
            fetch_redirect_response=False)

    def testFlaggedView(self):
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/flagged/", data={"c": pk})
        self.assertTemplateUsed(response, "comments/flagged.html")

    def testFlagSignals(self):
        """Test signals emitted by the comment flag view"""

        # callback
        def receive(sender, **kwargs):
            self.assertEqual(kwargs['flag'].flag, CommentFlag.SUGGEST_REMOVAL)
            self.assertEqual(kwargs['request'].user.username, "normaluser")
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.testFlagPost()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)


def makeModerator(username):
    u = User.objects.get(username=username)
    ct = ContentType.objects.get_for_model(Comment)
    p = Permission.objects.get(content_type=ct, codename="can_moderate")
    u.user_permissions.add(p)


class DeleteViewTests(CommentTestCase):

    def testDeletePermissions(self):
        """The delete view should only be accessible to 'moderators'"""
        comments = self.createSomeComments()
        pk = comments[0].pk

        # Test that we redirect to login page if not logged in.
        response = self.client.get("/delete/%d/" % pk)
        self.assertRedirects(response,
            "/accounts/login/?next=/delete/%d/" % pk,
            fetch_redirect_response=False)

        # Test that we return forbidden if you're logged in but don't have access.
        self.client.force_login(self.user)
        response = self.client.get("/delete/%d/" % pk)
        self.assertEqual(response.status_code, 403)

        makeModerator("normaluser")
        response = self.client.get("/delete/%d/" % pk)
        self.assertEqual(response.status_code, 200)

    def testDeletePost(self):
        """POSTing the delete view should mark the comment as removed"""
        comments = self.createSomeComments()
        pk = comments[0].pk
        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.post("/delete/%d/" % pk)
        self.assertRedirects(response, "/deleted/?c=%d" % pk)
        c = Comment.objects.get(pk=pk)
        self.assertTrue(c.is_removed)
        self.assertEqual(c.flags.filter(flag=CommentFlag.MODERATOR_DELETION, user__username="normaluser").count(), 1)

    def testDeletePostNext(self):
        """
        POSTing the delete view will redirect to an explicitly provided a next
        url.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.post("/delete/%d/" % pk, {'next': "/go/here/"})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)

    def testDeletePostUnsafeNext(self):
        """
        POSTing to the delete view with an unsafe next url will ignore the
        provided url when redirecting.
        """
        comments = self.createSomeComments()
        pk = comments[0].pk
        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.post("/delete/%d/" % pk,
            {'next': "http://elsewhere/bad"})
        self.assertRedirects(response, "/deleted/?c=%d" % pk)

    def testDeleteSignals(self):
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.testDeletePost()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)

    def testDeletedView(self):
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/deleted/", data={"c": pk})
        self.assertTemplateUsed(response, "comments/deleted.html")


class ApproveViewTests(CommentTestCase):

    def testApprovePermissions(self):
        """The approve view should only be accessible to 'moderators'"""
        comments = self.createSomeComments()
        pk = comments[0].pk

        # Test that we redirect to login page if not logged in.
        response = self.client.get("/approve/%d/" % pk)
        self.assertRedirects(
            response,
            "/accounts/login/?next=/approve/%d/" % pk,
            fetch_redirect_response=False
        )

        # Test that we return forbidden if you're logged in but don't have access.
        self.client.force_login(self.user)
        response = self.client.get("/approve/%d/" % pk)
        self.assertEqual(response.status_code, 403)

        # Verify that moderators can view this view.
        makeModerator("normaluser")
        response = self.client.get("/approve/%d/" % pk)
        self.assertEqual(response.status_code, 200)

    def testApprovePost(self):
        """POSTing the approve view should mark the comment as removed"""
        c1, c2, c3, c4 = self.createSomeComments()
        c1.is_public = False
        c1.save()

        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.post("/approve/%d/" % c1.pk)
        self.assertRedirects(response, "/approved/?c=%d" % c1.pk)
        c = Comment.objects.get(pk=c1.pk)
        self.assertTrue(c.is_public)
        self.assertEqual(c.flags.filter(flag=CommentFlag.MODERATOR_APPROVAL, user__username="normaluser").count(), 1)

    def testApprovePostNext(self):
        """
        POSTing the approve view will redirect to an explicitly provided a next
        url.
        """
        c1, c2, c3, c4 = self.createSomeComments()
        c1.is_public = False
        c1.save()

        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.post("/approve/%d/" % c1.pk,
            {'next': "/go/here/"})
        self.assertRedirects(response, "/go/here/?c=%d" % c1.pk, fetch_redirect_response=False)

    def testApprovePostUnsafeNext(self):
        """
        POSTing to the approve view with an unsafe next url will ignore the
        provided url when redirecting.
        """
        c1, c2, c3, c4 = self.createSomeComments()
        c1.is_public = False
        c1.save()

        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.post("/approve/%d/" % c1.pk,
            {'next': "http://elsewhere/bad"})
        self.assertRedirects(response, "/approved/?c=%d" % c1.pk)

    def testApproveSignals(self):
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.testApprovePost()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)

    def testApprovedView(self):
        comments = self.createSomeComments()
        pk = comments[0].pk
        response = self.client.get("/approved/", data={"c": pk})
        self.assertTemplateUsed(response, "comments/approved.html")


@override_settings(ROOT_URLCONF='testapp.urls_admin')
class AdminActionsTests(CommentTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Make "normaluser" a moderator
        cls.user.is_staff = True
        perms = Permission.objects.filter(
            content_type__app_label='django_comments',
            codename__endswith='comment'
        )
        for perm in perms:
            cls.user.user_permissions.add(perm)
        cls.user.save()

    def testActionsNonModerator(self):
        self.createSomeComments()
        self.client.force_login(self.user)
        response = self.client.get("/admin/django_comments/comment/")
        self.assertNotContains(response, "approve_comments")

    def testActionsModerator(self):
        self.createSomeComments()
        makeModerator("normaluser")
        self.client.force_login(self.user)
        response = self.client.get("/admin/django_comments/comment/")
        self.assertContains(response, "approve_comments")

    def testActionsDisabledDelete(self):
        "Tests a CommentAdmin where 'delete_selected' has been disabled."
        self.createSomeComments()
        self.client.force_login(self.user)
        response = self.client.get('/admin2/django_comments/comment/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<option value="delete_selected">')

    def performActionAndCheckMessage(self, action, action_params, expected_message):
        response = self.client.post('/admin/django_comments/comment/',
                                    data={'_selected_action': action_params,
                                          'action': action,
                                          'index': 0},
                                    follow=True)
        messages = list(m.message for m in response.context['messages'])
        self.assertTrue(expected_message in messages,
                     ("Expected message '%s' wasn't set (messages were: %s)" %
                        (expected_message, messages)))

    def testActionsMessageTranslations(self):
        c1, c2, c3, c4 = self.createSomeComments()
        one_comment = c1.pk
        many_comments = [c2.pk, c3.pk, c4.pk]
        makeModerator("normaluser")
        self.client.force_login(self.user)
        with translation.override('en'):
            # Test approving
            self.performActionAndCheckMessage('approve_comments', one_comment,
                '1 comment was successfully approved.')
            self.performActionAndCheckMessage('approve_comments', many_comments,
                '3 comments were successfully approved.')
            # Test flagging
            self.performActionAndCheckMessage('flag_comments', one_comment,
                '1 comment was successfully flagged.')
            self.performActionAndCheckMessage('flag_comments', many_comments,
                '3 comments were successfully flagged.')
            # Test removing
            self.performActionAndCheckMessage('remove_comments', one_comment,
                '1 comment was successfully removed.')
            self.performActionAndCheckMessage('remove_comments', many_comments,
                '3 comments were successfully removed.')
