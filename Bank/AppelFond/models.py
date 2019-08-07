from Bank.utils import STATUT, ROLES, TYPE
import jwt
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager, PermissionsMixin)


class Tbanque(models.Model):
    nom_banq = models.CharField(max_length=30, blank=True, null=True)
    code_banq = models.CharField(max_length=30, blank=True, null=True)
    code_agence = models.CharField(max_length=30, blank=True, null=True)
    #plafond = models.ForeignKey(TPlafond, on_delete=models.CASCADE)
    url_core = models.CharField(max_length=30, blank=True, null=True)

    objects = models.Manager()

    #def __str__(self):
    #    return self.nom_banq

    class Meta:
        managed = True
        db_table = 'Tbanque'

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
        user.save()
        return user

    # def create_superuser(self, username, email, password):
    #     if password is None:
    #         raise TypeError('Superusers must have a password.')
    #     user = self.create_user(username, email, password)
    #     user.is_superuser = True
    #     user.is_staff = True
    #     user.save()
    #     return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    phone = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLES,blank=True, null=True)
    banque = models.ForeignKey(Tbanque, on_delete=models.CASCADE,null=True, blank=True,)
    type_plafond = models.CharField(max_length=50, choices=TYPE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def _generate_jwt_token(self):
        #dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            #'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')






# class User(AbstractUser):
#     phone = models.IntegerField(blank=True, null=True)
#     role = models.CharField(max_length=50, choices=ROLES,blank=True, null=True)
#     banque = models.ForeignKey(Tbanque, on_delete=models.CASCADE,null=True, blank=True,)
#     type_plafond = models.CharField(max_length=50, choices=TYPE,blank=True, null=True)
#
#     #def __str__(self):
#     #    return self.email


class TPlafond(models.Model):
    montant_max = models.FloatField(blank=True, null=True)
    montant_min = models.FloatField(blank=True, null=True)
    montant_cumul_max_week = models.FloatField(blank=True, null=True)
    montant_cumul_max_month = models.FloatField(blank=True, null=True)
    seuil_validation = models.FloatField(blank=True, null=True)
    client_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    banque_id = models.OneToOneField(Tbanque, on_delete=models.CASCADE, blank=True, null=True)
    libelle = models.CharField(max_length=50)

    #def __str__(self):
    #    return self.libelle

    class Meta:
        managed = True
        db_table = 'TPlafond'



class TappelFonds(models.Model):
    montant = models.FloatField(blank=False, null=False)
    date = models.DateField(auto_now_add=True)
    compte_id = models.CharField(max_length=10)
    compte_numero = models.IntegerField()
    numero_recharge = models.IntegerField()
    client_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    client_nom = models.CharField(max_length=10)
    client_prenom = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(choices=STATUT, max_length=20)
    banque_id = models.ForeignKey(Tbanque, on_delete=models.CASCADE,null=True, blank=True,)

    #def __str__(self):
    #    return self.client_nom

    class Meta:
        managed = True
        db_table = 'TappelFonds'