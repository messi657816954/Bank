from django.contrib import admin
from AppelFond.models import *
# Register your models here.

from django.contrib.auth.admin import UserAdmin

from AppelFond.models import User
from Account.forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *





class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'username','phone','role','password']

admin.site.register(User, CustomUserAdmin)

admin.site.register(Tbanque)
admin.site.register(TPlafond)
admin.site.register(TappelFonds)




