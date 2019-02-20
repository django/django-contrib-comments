from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0002_update_user_email_field_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='submit_date',
            field=models.DateTimeField(default=None, verbose_name='date/time submitted', db_index=True),
            preserve_default=True,
        ),
    ]
