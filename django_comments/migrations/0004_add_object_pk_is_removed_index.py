from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0003_add_submit_date_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='is_removed',
            field=models.BooleanField(
                db_index=True, default=False,
                help_text='Check this box if the comment is inappropriate. '
                          'A "This comment has been removed" message will be displayed instead.',
                verbose_name='is removed'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='object_pk',
            field=models.CharField(max_length=64, db_index=True, verbose_name='object ID'),
        ),
    ]
