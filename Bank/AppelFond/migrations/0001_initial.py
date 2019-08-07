# Generated by Django 2.2 on 2019-08-02 10:20

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tbanque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_banq', models.CharField(blank=True, max_length=30, null=True)),
                ('code_banq', models.CharField(blank=True, max_length=30, null=True)),
                ('code_agence', models.CharField(blank=True, max_length=30, null=True)),
                ('url_core', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.IntegerField(blank=True, null=True)),
                ('role', models.CharField(blank=True, choices=[('ADMIN', 'ADMIN'), ('CLIENT', 'CLIENT')], max_length=50, null=True)),
                ('banque', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='AppelFond.Tbanque')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TPlafond',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_max', models.FloatField(blank=True, null=True)),
                ('montant_min', models.FloatField(blank=True, null=True)),
                ('montant_cumul_max_week', models.FloatField(blank=True, null=True)),
                ('montant_cumul_max_month', models.FloatField(blank=True, null=True)),
                ('seuil_validation', models.FloatField(blank=True, null=True)),
                ('libelle', models.CharField(max_length=10)),
                ('client_id', models.ForeignKey(db_column='client_id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TappelFonds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('compte_id', models.CharField(max_length=10)),
                ('compte_numero', models.IntegerField(max_length=10)),
                ('numero_recharge', models.IntegerField(max_length=10)),
                ('client_nom', models.CharField(max_length=10)),
                ('client_prenom', models.CharField(blank=True, max_length=20, null=True)),
                ('status', models.CharField(choices=[('CANCEL', 'CANCEL'), ('PROGRESS', 'PROGRESS'), ('WAIT', 'WAIT'), ('FINISH', 'FINISH')], max_length=20)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
