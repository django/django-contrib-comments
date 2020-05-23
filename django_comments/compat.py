"""
Module to store compatiblity imports to prevent Django deprecation warnings.
"""
try:
    # Introduced in Django 3.0.
    from django.utils.http import url_has_allowed_host_and_scheme
except ImportError:
    from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme
