# Generated by Django 3.0.8 on 2020-08-07 13:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20200807_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='created_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
