from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from api import models

class UserAdmin(BaseUserAdmin):
    '''
    Custom user admin
    '''
    ordering = ["id"]
    list_display = ["email", "name"]

admin.site.register(models.User, UserAdmin)