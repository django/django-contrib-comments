"""
A few bits of helper functions for comment views.
"""

import textwrap
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.core.exceptions import ObjectDoesNotExist

from ..compat import url_has_allowed_host_and_scheme

import django_comments


def next_redirect(request, fallback, **get_kwargs):
    """
    Handle the "where should I go next?" part of comment views.

    The next value could be a
    ``?next=...`` GET arg or the URL of a given view (``fallback``). See
    the view modules for examples.

    Returns an ``HttpResponseRedirect``.
    """
    next = request.POST.get('next')
    if not url_has_allowed_host_and_scheme(url=next, allowed_hosts={request.get_host()}):
        next = resolve_url(fallback)

    if get_kwargs:
        if '#' in next:
            tmp = next.rsplit('#', 1)
            next = tmp[0]
            anchor = '#' + tmp[1]
        else:
            anchor = ''

        joiner = ('?' in next) and '&' or '?'
        next += joiner + urlencode(get_kwargs) + anchor
    return HttpResponseRedirect(next)


def confirmation_view(template, doc="Display a confirmation view."):
    """
    Confirmation view generator for the "comment was
    posted/flagged/deleted/approved" views.
    """

    def confirmed(request):
        comment = None
        if 'c' in request.GET:
            try:
                comment = django_comments.get_model().objects.get(pk=request.GET['c'])
            except (ObjectDoesNotExist, ValueError):
                pass
        return render(request, template, {'comment': comment})

    confirmed.__doc__ = textwrap.dedent("""\
        %s

        Templates: :template:`%s``
        Context:
            comment
                The posted comment
        """ % (doc, template)
    )
    return confirmed
