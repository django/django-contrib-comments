.. :changelog:

History
=======

X.Y.Z (YYYY-MM-DD)
------------------

* Added testing for Python 3.7.

1.9.0 (2018-08-04)
------------------

* Added testing for Python 3.6.
* Confirmed support for Django 2.0 and 2.1.
* Dropped support for Django < 1.11.
* ``ip_address`` is set to None when ``REMOTE_ADDR`` is empty (#93).

1.8.0 (2017-02-03)
------------------

* Fixed a packaging error which caused sub-packages of the tests to be
  distributed.
* Use ``get_current_site`` to look up the site instead of ``settings.SITE_ID``.
* Confirmed support for Django 1.11.
* Dropped Django 1.7 and Python 3.2/3.3 support.
* Added testing for Python 3.5.
* Updated translations.

1.7.3 (2016-09-13)
------------------

* Fixed a regression which prevented the ``Comment`` model
  from registering with the admin.
* Updated translations.

1.7.2 (2016-08-04)
------------------

* ``get_comment_list`` now returns a ``QuerySet`` instead of a ``list``.
* Fixed a Django 1.9+ compatibility issue with a customized comment app in
  ``INSTALLED_APPS`` (#87).
* Confirmed support for Django 1.10.

1.7.1 (2016-05-03)
------------------

* Isolated abstract models outside of models.py so they can be imported without
  triggering Django's deprecation warning about models living outside of a
  'models' module.
* Updated translations.

1.7.0 (2016-03-29)
------------------

* Dropped Django 1.6 and Python 2.6 support
* Improved usage of ``AppConfig`` functionality for custom models.
* Added ``CommentAbstractModel`` as another abstract model layer for easier
  customization.
* Avoided N+1 query problem for users on comments.
* Made the moderation email subject translatable.
* Added a database index to ``Comment.submit_date``, since it is used for the
  default ordering.
* Fixed packaging so locale files are distributed.
* Updated translations.

1.6.2 (2016-12-10)
------------------

* Fixed some Django deprecation warnings.
* Setup translation system using Transifex.
* Added missing South migration for the email length.
* Updated translations.

1.6.1 (2016-05-08)
------------------

* Fixed migrations not working when installed as an egg.


1.6.0 (2016-04-29)
------------------

* Made ``CommentSecurityForm`` pass keyword arguments to its parent class.
* Added ``COMMENTS_TIMEOUT`` setting to configure the timeout for
  ``CommentSecurityForm``.
* Migrated ``Comment.user_email`` to 254 characters.
* Moved South migrations to ``south_migrations`` folder so they can exist with
  Django 1.7 migrations.
* Added Django 1.9 compatibility, dropped support for Django 1.5.
