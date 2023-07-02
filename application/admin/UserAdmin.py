from password_generator import PasswordGenerator

from packages.experimental.hubi_admin.action_components import Action
from packages.experimental.hubi_admin.form_components import TextInput, Checkbox, Toggle
from packages.experimental.hubi_admin.metrics import Metric
from packages.experimental.hubi_admin.table_components import BooleanColumn, TextColumn


class UserAdmin:
    menu_icon = "fa-user"
    preview_field = "fullname"
    model_label = "Employee"
    navigation_label = "Employees"
    table_polling = True
    poll_interval = 1


    def get_header_metrics(self):
        from application.models.User import User
        return [
            Metric.make("# Active Clients").value(User.where("is_disabled", 0).get().count()).render(),
            Metric.make("# Approvers").value(User.where("is_approver", "on").get().count()).render(),
            Metric.make("# Approvers").value(User.where("is_admin", "on").get().count()).render(),
        ]

    def get_fillable(self):
        return [
            Checkbox.make("is_admin").label("Is Admin").render(),
            Checkbox.make("is_approver").label("Is Approver").render(),
            Checkbox.make("is_reviewer").label("Is Reviewer").render(),
            Checkbox.make("is_disabled").label("Is Disabled").colspan(6).render(),
            TextInput.make("fullname").placeholder("Fullname").label("Fullname").required().render(),
            TextInput.make("username").placeholder("Username").label("Username").required().render(),
            TextInput.make("email").placeholder("Email").label("Email").required().render(),
            TextInput.make("encrypted_password").placeholder("Password").label("Password").default(
                PasswordGenerator().generate()).required().render(),
        ]

    def get_table_columns(self):
        return [
            TextColumn.make("fullname").label("Fullname").render(),
            TextColumn.make("username").label("Username").render(),
            TextColumn.make("email").label("Email").render(),
            BooleanColumn.make("is_admin").label("Is Admin").editable().render(),
            BooleanColumn.make("is_approver").label("Is Approver").editable().render(),
            BooleanColumn.make("is_reviewer").label("Is Reviewer").editable().render(),
            BooleanColumn.make("is_disabled").label("Is Disabled").editable().render(),
            TextColumn.make("login_count").label("Login Count").render(),
            TextColumn.make("last_login_ip").label("Last Login IP").default("Not Available").render(),
        ]  # "id", "username", "is_admin", "is_approver", "is_disabled", "login_count", "last_login_ip"

    def get_table_actions(self):
        return [

        ]

    __admin_list_filter__ = "id"  # Filter field for resource
    __admin_search_field__ = ["username", "fullname"]  # Search field for resource

    def get_relations(self):
        return []

    __admin_edit_actions__ = [
        # {"name": "Delete", "label": "Delete", "view": "admin.index", "color": "warning", "url": "/admin/records/{{ id }}/delete"},
        # {"name": "Change_Status", "label": "Change Status", "view": "admin.index", "color": "info", "url": "/admin/records/{{ id }}/delete", "html": "<h1>Change Status</h1>"},
    ]

    def before_create(self, data):
        return data

    def after_create(self, model):
        return model

    def before_edit(self, data):
        return data

    def after_edit(self, model):
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
