from django import template
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_text

import django_comments

register = template.Library()


class BaseCommentNode(template.Node):
    """
    Base helper class (abstract) for handling the get_comment_* template tags.
    Looks a bit strange, but the subclasses below should make this a bit more
    obvious.
    """

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse get_comment_list/count/form and return a Node."""
        tokens = token.split_contents()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% get_whatever for obj as varname %}
        if len(tokens) == 5:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError("Third argument in %r must be 'as'" % tokens[0])
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                as_varname=tokens[4],
            )

        # {% get_whatever for app.model pk as varname %}
        elif len(tokens) == 6:
            if tokens[4] != 'as':
                raise template.TemplateSyntaxError("Fourth argument in %r must be 'as'" % tokens[0])
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5]
            )

        else:
            raise template.TemplateSyntaxError("%r tag requires 4 or 5 arguments" % tokens[0])

    @staticmethod
    def lookup_content_type(token, tagname):
        try:
            app, model = token.split('.')
            return ContentType.objects.get_by_natural_key(app, model)
        except ValueError:
            raise template.TemplateSyntaxError("Third argument in %r must be in the format 'app.model'" % tagname)
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError("%r tag has non-existant content-type: '%s.%s'" % (tagname, app, model))

    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None, as_varname=None, comment=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError(
                "Comment nodes must be given either a literal object or a ctype and object pk.")
        self.comment_model = django_comments.get_model()
        self.as_varname = as_varname
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr
        self.comment = comment

    def render(self, context):
        qs = self.get_queryset(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ''

    def get_queryset(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        # Explicit SITE_ID takes precedence over request. This is also how
        # get_current_site operates.
        site_id = getattr(settings, "SITE_ID", None)
        if not site_id and ('request' in context):
            site_id = get_current_site(context['request']).pk

        qs = self.comment_model.objects.filter(
            content_type=ctype,
            object_pk=smart_text(object_pk),
            site__pk=site_id,
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in self.comment_model._meta.fields]
        if 'is_public' in field_names:
            qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)
        if 'user' in field_names:
            qs = qs.select_related('user')
        return qs

    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_pk_expr.resolve(context, ignore_failures=True)

    def get_context_value_from_queryset(self, context, qs):
        """Subclasses should override this."""
        raise NotImplementedError


class CommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""

    def get_context_value_from_queryset(self, context, qs):
        return qs


class CommentCountNode(BaseCommentNode):
    """Insert a count of comments into the context."""

    def get_context_value_from_queryset(self, context, qs):
        return qs.count()


class CommentFormNode(BaseCommentNode):
    """Insert a form for the comment model into the context."""

    def get_form(self, context):
        obj = self.get_object(context)
        if obj:
            return django_comments.get_form()(obj)
        else:
            return None

    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None
        else:
            object_pk = self.object_pk_expr.resolve(context,
                                                    ignore_failures=True)
            return self.ctype.get_object_for_this_type(pk=object_pk)

    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ''


class RenderCommentFormNode(CommentFormNode):
    """Render the comment form directly"""

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_comment_form and return a Node."""
        tokens = token.split_contents()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_comment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/form.html" % (ctype.app_label, ctype.model),
                "comments/%s/form.html" % ctype.app_label,
                "comments/form.html"
            ]
            context_dict = context.flatten()
            context_dict['form'] = self.get_form(context)
            formstr = render_to_string(template_search_list, context_dict)
            return formstr
        else:
            return ''


class RenderCommentListNode(CommentListNode):
    """Render the comment list directly"""

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_comment_list and return a Node."""
        tokens = token.split_contents()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_list for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_comment_list for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/list.html" % (ctype.app_label, ctype.model),
                "comments/%s/list.html" % ctype.app_label,
                "comments/list.html"
            ]
            qs = self.get_queryset(context)
            context_dict = context.flatten()
            context_dict['comment_list'] = self.get_context_value_from_queryset(context, qs)
            liststr = render_to_string(template_search_list, context_dict)
            return liststr
        else:
            return ''


# We could just register each classmethod directly, but then we'd lose out on
# the automagic docstrings-into-admin-docs tricks. So each node gets a cute
# wrapper function that just exists to hold the docstring.

@register.tag
def get_comment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_count for [object] as [varname]  %}
        {% get_comment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comment_count for event as comment_count %}
        {% get_comment_count for calendar.event event.id as comment_count %}
        {% get_comment_count for calendar.event 17 as comment_count %}

    """
    return CommentCountNode.handle_token(parser, token)


@register.tag
def get_comment_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_list for [object] as [varname]  %}
        {% get_comment_list for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comment_list for event as comment_list %}
        {% for comment in comment_list %}
            ...
        {% endfor %}

    """
    return CommentListNode.handle_token(parser, token)


@register.tag
def render_comment_list(parser, token):
    """
    Render the comment list (as returned by ``{% get_comment_list %}``)
    through the ``comments/list.html`` template

    Syntax::

        {% render_comment_list for [object] %}
        {% render_comment_list for [app].[model] [object_id] %}

    Example usage::

        {% render_comment_list for event %}

    """
    return RenderCommentListNode.handle_token(parser, token)


@register.tag
def get_comment_form(parser, token):
    """
    Get a (new) form object to post a new comment.

    Syntax::

        {% get_comment_form for [object] as [varname] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] %}
    """
    return CommentFormNode.handle_token(parser, token)


@register.tag
def render_comment_form(parser, token):
    """
    Render the comment form (as returned by ``{% render_comment_form %}``) through
    the ``comments/form.html`` template.

    Syntax::

        {% render_comment_form for [object] %}
        {% render_comment_form for [app].[model] [object_id] %}
    """
    return RenderCommentFormNode.handle_token(parser, token)


@register.simple_tag
def comment_form_target():
    """
    Get the target URL for the comment form.

    Example::

        <form action="{% comment_form_target %}" method="post">
    """
    return django_comments.get_form_target()


@register.simple_tag
def get_comment_permalink(comment, anchor_pattern=None):
    """
    Get the permalink for a comment, optionally specifying the format of the
    named anchor to be appended to the end of the URL.

    Example::
        {% get_comment_permalink comment "#c%(id)s-by-%(user_name)s" %}
    """

    if anchor_pattern:
        return comment.get_absolute_url(anchor_pattern)
    return comment.get_absolute_url()
