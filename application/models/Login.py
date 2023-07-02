from masoniteorm.models import Model

from application.admin.LoginAdmin import LoginAdmin


class Login(Model, LoginAdmin):
    __table__ = "login"

