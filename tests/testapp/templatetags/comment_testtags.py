from django.template import Library

register = Library()


@register.filter
def noop(variable, param=None):
    return variable
