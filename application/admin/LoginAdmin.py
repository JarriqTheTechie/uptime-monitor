
from packages.experimental.hubi_admin.action_components import Action
from packages.experimental.hubi_admin.form_components import FileUpload, Repeater, TextInput, Select
from packages.experimental.hubi_admin.metrics import Metric
from packages.experimental.hubi_admin.notification_component import Notification
from packages.experimental.hubi_admin.table_components import BadgeColumn, BooleanColumn, TextColumn

class LoginAdmin:
    menu_icon = "fa-users-viewfinder"
    display_in_nav = True # Display resource in navigation
    table_polling = False
    table_polling_interval = 5 # seconds

    def get_header_metrics(self):
        from application.models.Login import Login
        return [
            Metric.make("number_logins").heading("# Logins").value(Login.select(['ip', 'username']).distinct().get().count()).render(),
        ]

    def get_fillable(self): return [
        TextInput.make("username").placeholder("Username").label("Username").required().render(),
        TextInput.make("ip").placeholder("IP Address").label("IP Address").required().render(),
    ]

    def get_table_columns(self):
        return [
            TextColumn.make("username").label("Username").render(),
            TextColumn.make("ip").label("IP Address").render(),
            TextColumn.make("last_login").label("Last Login Time").render(),
        ]

    __admin_list_filter__ = "id" # Filter field for resource
    __admin_search_field__ = ["username", "ip", "last_login"] # Search field for resource

    def get_relations(self):
        return []

    def admin_actions(self): return [

    ]

    def before_create(self, data):
        return data

    def after_create(self, model):
        return model

    def before_edit(self, data):
        return data

    def after_edit(self, model):
        Notification.make("Record").title("").body("").info().send()
        return model

    # Permissions

    def can_list(self) -> bool:
        pass

    def can_view(self) -> bool:
        pass

    def can_edit(self) -> bool:
        pass

    def can_create(self) -> bool:
        pass

    def can_delete(self) -> bool:
        pass

    def can_export(self) -> bool:
        pass

    def can_import(self) -> bool:
        pass

    def can_filter(self) -> bool:
        pass
