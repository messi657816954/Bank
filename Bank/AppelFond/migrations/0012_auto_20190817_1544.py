# Generated by Django 2.2 on 2019-08-17 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppelFond', '0011_auto_20190812_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tappelfonds',
            name='status',
            field=models.CharField(choices=[('CANCEL', 'CANCEL'), ('PROGRESS', 'PROGRESS'), ('WAIT', 'WAIT'), ('FINISH', 'FINISH'), ('SUCESS', 'SUCESS')], max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('ADMIN', 'ADMIN'), ('CLIENT', 'CLIENT')], max_length=50, null=True),
        ),
    ]
