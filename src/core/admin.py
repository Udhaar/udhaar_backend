from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

from django.utils.translation import gettext as _


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name",)}),
        (
            _("Permissions"),
            {
                "fields": ("is_active", "is_staff", "is_superuser")
            }
        ),
        (_("Important Dates"), {
         "fields": ('last_login', 'last_modified_date',)})
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2")
        }),
    )


admin.site.register(User, UserAdmin)
