from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from api import models
from django.utils.translation import gettext as _


class UserAdmin(BaseUserAdmin):
    '''
    Custom user admin
    '''
    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (("Personal Info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")}
        ),
        (("Important dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ("last_login",)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "name",
                "is_staff", "is_superuser", "is_active"
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Destination)
admin.site.register(models.Tag)
admin.site.register(models.Feature)
