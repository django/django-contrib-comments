#!/usr/bin/env python

"""
Adapted from django-constance, which itself was adapted from django-adminfiles.
"""

import os
import sys
import django

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path[0:0] = [here, parent]

from django.conf import settings
settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.admin",
        "django_comments",
        "testapp",
        "custom_comments",
    ],
    MIDDLEWARE=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    ROOT_URLCONF='testapp.urls',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ]
            },
        },
    ],
    SECRET_KEY="it's a secret to everyone",
    SITE_ID=1,
)

from django.test.runner import DiscoverRunner


def main(test_labels=None):
    django.setup()
    runner = DiscoverRunner(failfast=True, verbosity=1)
    failures = runner.run_tests(test_labels or ['testapp'], interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    test_labels = None
    if len(sys.argv) > 1:
        test_labels = sys.argv[1:]
    main(test_labels)
