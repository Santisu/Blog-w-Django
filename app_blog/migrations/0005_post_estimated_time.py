# Generated by Django 4.2.4 on 2023-08-17 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_blog', '0004_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='estimated_time',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
