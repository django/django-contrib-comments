from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user_email',
            field=models.EmailField(
                max_length=254, verbose_name="user's email address",
                blank=True),
        ),
    ]
