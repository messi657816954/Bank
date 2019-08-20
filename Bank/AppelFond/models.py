
from Configurations.utils import STATUT, ROLES, TYPE
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager, PermissionsMixin)
from rest_framework.authtoken.models import Token


class Tbanque(models.Model):
    nom_banque = models.CharField(max_length=30, blank=True, null=True)
    code_banque = models.CharField(max_length=30, blank=True, null=True)
    code_agence = models.CharField(max_length=30, blank=True, null=True)
    #plafond = models.ForeignKey(TPlafond, on_delete=models.CASCADE)
    url_core = models.CharField(max_length=30, blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
       return self.nom_banq

    class Meta:
        ordering = ['-id']
    #     db_table = 'Tbanque'

class UserManager(BaseUserManager):
    def create_user(self, username, email,phone,role,banque,type_plafond, password=None):
        if username is None:
            raise TypeError('Users must have a username.')
        if email is None:
            raise TypeError('Users must have an email address.')
        user = self.model(username=username,
                         email=self.normalize_email(email),
                         phone=phone,
                         role=role,
                         banque=banque,
                        type_plafond=type_plafond)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password):
        user = self.model(username=username,
                          email=self.normalize_email(email),
                          )
        user.set_password(password)
        user.staff=True
        user.admin=True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    phone = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLES,blank=True, null=True)
    banque = models.ForeignKey(Tbanque, on_delete=models.CASCADE,null=True, blank=True,)
    type_plafond = models.CharField(max_length=50, choices=TYPE, blank=True, null=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    def _generate_jwt_token(self):
        token = Token.objects.get_or_create(user=self)
        return token

class TPlafond(models.Model):
    montant_max = models.FloatField(blank=True, null=True)
    montant_min = models.FloatField(blank=True, null=True)
    montant_cumul_max_week = models.FloatField(blank=True, null=True)
    montant_cumul_max_month = models.FloatField(blank=True, null=True)
    seuil_validation = models.FloatField(blank=True, null=True)
    client_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    banque_id = models.OneToOneField(Tbanque, on_delete=models.CASCADE, blank=True, null=True)
    libelle = models.CharField(max_length=50)

    def __str__(self):
       return self.libelle

    class Meta:
        managed = True
        db_table = 'TPlafond'



class TappelFonds(models.Model):
    montant = models.FloatField(blank=False, null=False)
    date = models.DateField(auto_now_add=True)
    compte_id = models.CharField(max_length=10)
    compte_numero = models.CharField(max_length=30)
    numero_recharge = models.CharField(max_length=30)
    client_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    client_nom = models.CharField(max_length=10)
    client_prenom = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(choices=STATUT, max_length=20)
    banque_id = models.ForeignKey(Tbanque, on_delete=models.CASCADE,null=True, blank=True,)

    objects = models.Manager()

    def __str__(self):
       return self.client_nom

    class Meta:
        managed = True
        db_table = 'TappelFonds'