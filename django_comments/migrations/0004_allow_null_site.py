# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0003_add_submit_date_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='site',
            field=models.ForeignKey(to='sites.Site', on_delete=models.CASCADE, null=True),
            preserve_default=True,
        ),
    ]
