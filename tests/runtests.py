#!/usr/bin/env python

"""
Adapted from django-constance, which itself was adapted from django-adminfiles.
"""

import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path[0:0] = [here, parent]

from django.conf import settings
settings.configure(
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}},
    INSTALLED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.admin",
        "django_comments",
        "testapp",
        "custom_comments",
    ],
    ROOT_URLCONF = 'testapp.urls',
    SECRET_KEY = "it's a secret to everyone",
    SITE_ID = 1,
)

from django.test.simple import DjangoTestSuiteRunner

def main():
    runner = DjangoTestSuiteRunner(failfast=True, verbosity=1)
    failures = runner.run_tests(['testapp'], interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    main()
