from urllib.parse import urlencode

from django import http
from django.apps import apps
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.shortcuts import render, resolve_url

from ..compat import url_has_allowed_host_and_scheme

import django_comments
from django_comments import signals
from django_comments.views.utils import confirmation_view


class BadRequest(Exception):
    """
    Exception raised for a bad post request holding the CommentPostBadRequest
    object.
    """
    def __init__(self, response):
        self.response = response


class CommentPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """

    def __init__(self, why):
        super().__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})


class CommentPostView(FormView):
    http_method_names = ['post']

    def get_target_object(self, data):
        # Look up the object we're trying to comment about
        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
        if ctype is None or object_pk is None:
            raise BadRequest(CommentPostBadRequest("Missing content_type or object_pk field."))
        try:
            model = apps.get_model(*ctype.split(".", 1))
            return model._default_manager.using(self.kwargs.get('using')).get(pk=object_pk)
        except TypeError:
            raise BadRequest(CommentPostBadRequest(
                "Invalid content_type value: %r" % escape(ctype)))
        except AttributeError:
            raise BadRequest(CommentPostBadRequest(
                "The given content-type %r does not resolve to a valid model." % escape(ctype)))
        except ObjectDoesNotExist:
            raise BadRequest(CommentPostBadRequest(
                "No object matching content-type %r and object PK %r exists." % (
                    escape(ctype), escape(object_pk))))
        except (ValueError, ValidationError) as e:
            raise BadRequest(CommentPostBadRequest(
                "Attempting to get content-type %r and object PK %r raised %s" % (
                    escape(ctype), escape(object_pk), e.__class__.__name__)))

    def get_form_kwargs(self):
        data = self.request.POST.copy()
        if self.request.user.is_authenticated:
            if not data.get('name', ''):
                data["name"] = self.request.user.get_full_name() or self.request.user.get_username()
            if not data.get('email', ''):
                data["email"] = self.request.user.email
        return data

    def get_form_class(self):
        """Return the form class to use."""
        return django_comments.get_form()

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.target_object, data=self.data)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        fallback = self.kwargs.get('next') or 'comments-comment-done'
        get_kwargs = dict(c=self.object._get_pk_val())
        next = self.request.POST.get('next')

        if not url_has_allowed_host_and_scheme(url=next, allowed_hosts={self.request.get_host()}):
            next = resolve_url(fallback)

        if '#' in next:
            tmp = next.rsplit('#', 1)
            next = tmp[0]
            anchor = '#' + tmp[1]
        else:
            anchor = ''

        joiner = ('?' in next) and '&' or '?'
        next += joiner + urlencode(get_kwargs) + anchor

        return next

    def create_comment(self, form):
        comment = form.get_comment_object(site_id=get_current_site(self.request).id)
        comment.ip_address = self.request.META.get("REMOTE_ADDR", None) or None
        if self.request.user.is_authenticated:
            comment.user = self.request.user

        # Signal that the comment is about to be saved
        responses = signals.comment_will_be_posted.send(
            sender=comment.__class__,
            comment=comment,
            request=self.request
        )

        for (receiver, response) in responses:
            if response is False:
                raise BadRequest(CommentPostBadRequest(
                    "comment_will_be_posted receiver %r killed the comment" % receiver.__name__))

        # Save the comment and signal that it was saved
        comment.save()
        signals.comment_was_posted.send(
            sender=comment.__class__,
            comment=comment,
            request=self.request
        )
        return comment

    def form_invalid(self, form):
        model = type(self.target_object)
        template_list = [
            # These first two exist for purely historical reasons.
            # Django v1.0 and v1.1 allowed the underscore format for
            # preview templates, so we have to preserve that format.
            "comments/%s_%s_preview.html" % (model._meta.app_label, model._meta.model_name),
            "comments/%s_preview.html" % model._meta.app_label,
            # Now the usual directory based template hierarchy.
            "comments/%s/%s/preview.html" % (model._meta.app_label, model._meta.model_name),
            "comments/%s/preview.html" % model._meta.app_label,
            "comments/preview.html",
        ]
        return render(self.request, template_list, {
                "comment": form.data.get("comment", ""),
                "form": form,
                "next": self.data.get("next", self.kwargs.get('next')),
            },
        )

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, **kwargs):
        self.object = None
        self.target_object = None
        self.data = self.get_form_kwargs()
        try:
            self.target_object = self.get_target_object(self.data)
        except BadRequest as exc:
            return exc.response

        form = self.get_form()

        # Check security information
        if form.security_errors():
            return CommentPostBadRequest(
                "The comment form failed security verification: %s" % escape(str(form.security_errors())))

        if not form.is_valid() or "preview" in self.data:
            return self.form_invalid(form)
        else:
            try:
                self.object = self.create_comment(form)
            except BadRequest as exc:
                return exc.response
            else:
                return self.form_valid(form)


comment_done = confirmation_view(
    template="comments/posted.html",
    doc="""Display a "comment was posted" success page."""
)
