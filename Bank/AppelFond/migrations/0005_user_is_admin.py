# Generated by Django 2.2 on 2019-08-10 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppelFond', '0004_auto_20190808_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
