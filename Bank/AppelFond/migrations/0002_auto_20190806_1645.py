# Generated by Django 2.2 on 2019-08-06 15:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('AppelFond', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tappelfonds',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='tbanque',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='tplafond',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
        migrations.AddField(
            model_name='tappelfonds',
            name='banque_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='AppelFond.Tbanque'),
        ),
        migrations.AddField(
            model_name='tplafond',
            name='banque_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='AppelFond.Tbanque'),
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='type_plafond',
            field=models.CharField(blank=True, choices=[('USER', 'USER'), ('BANK', 'BANK')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='tplafond',
            name='client_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tplafond',
            name='libelle',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterModelTable(
            name='tappelfonds',
            table='TappelFonds',
        ),
        migrations.AlterModelTable(
            name='tbanque',
            table='Tbanque',
        ),
        migrations.AlterModelTable(
            name='tplafond',
            table='TPlafond',
        ),
    ]
