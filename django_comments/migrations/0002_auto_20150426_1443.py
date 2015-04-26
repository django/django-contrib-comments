# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='is_removed',
            field=models.BooleanField(
                default=False,
                help_text='Check this box if the comment is inappropriate. '
                          'A "This comment has been removed" message will be '
                          'displayed instead.',
                verbose_name='is removed'
            ),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user_email',
            field=models.EmailField(
                max_length=254, verbose_name="user's email address",
                blank=True),
        ),
    ]
