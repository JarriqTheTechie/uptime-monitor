from masoniteorm.models import Model

from application.admin.UserAdmin import UserAdmin


class User(Model, UserAdmin):
    __casts__ = {
        "is_admin": "bool",
        "is_approver": "bool",
        "is_disabled": "bool",
    }

