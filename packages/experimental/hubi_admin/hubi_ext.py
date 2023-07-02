from flask import render_template, request
from exceptionite.flask import ExceptioniteReporter
import inspect
import os
import datetime
import click
import inflection
import jinja2
import markupsafe
import werkzeug
import yaml

from helpers import to_class
from packages.experimental.mv_components.mv_components import MVComponent
from packages.stable.flask_fs_router import FlaskFSRouter
from packages.stable.masonite_audit.providers import AuditProvider


def HubiAdmin(app, secret_key=os.urandom(24)):
    loader = jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.FileSystemLoader("packages/experimental/hubi_admin/templates"),
        ]
    )
    app.jinja_env.loader = loader
    app.jinja_options["undefined"] = jinja2.ChainableUndefined
    FlaskFSRouter(app)
    MVComponent(app)
    AuditProvider()
    app.secret_key = secret_key

    @app.errorhandler(Exception)
    def handle_exception(exception):
        handler = ExceptioniteReporter(exception, request)
        # display exception stack trace nicely in console
        handler.terminal()
        return handler.html()

    @app.errorhandler(403)
    def forbidden(e):
        error = {
            "title": "Unauthorized Access",
            "message": e,
        }
        return render_template('components/layouts/DefaultErrorPage.html', error=error), 403

    @app.errorhandler(404)
    def forbidden(e):
        error = {
            "title": "Page Not Found",
            "message": e,
        }
        return render_template('components/layouts/DefaultErrorPage.html', error=error), 403

    def getByDot(obj, ref):
        """
        Use MongoDB style 'something.by.dot' syntax to retrieve objects from Python dicts.

        This also accepts nested arrays, and accommodates the '.XX' syntax that variety.js
        produces.

        Usage:
           >>> x = {"top": {"middle" : {"nested": "value"}}}
           >>> q = 'top.middle.nested'
           >>> getByDot(x,q)
           "value"
        """
        val = obj
        tmp = ref
        ref = tmp.replace(".XX", "[0]")
        if tmp != ref:
            print("Warning: replaced '.XX' with [0]-th index")
        for key in ref.split('.'):
            idstart = key.find("[")
            embedslist = 1 if idstart > 0 else 0
            if embedslist:
                idx = int(key[idstart + 1:key.find("]")])
                kyx = key[:idstart]
                try:
                    val = val[kyx][idx]
                except IndexError:
                    print("Index: x['{}'][{}] does not exist.".format(kyx, idx))
                    raise
            else:
                if val:
                    val = val[key]
                else:
                    val = None
        return (val)

    @app.template_global()
    def from_config(key):
        config = yaml.load(open("config/config.yaml", "r"), Loader=yaml.FullLoader)
        return getByDot(config, key)

    @app.template_global()
    def model_key(model, key):
        try:
            if type(getByDot(model, key)).__name__ != "method":
                return getByDot(model, key)
            else:
                return getByDot(model, key)()
        except AttributeError:
            return None
        except KeyError:
            return None

    @app.template_global()
    def get_class(name, directory="models"):
        if directory == "models":
            return to_class(f'application.{directory}.{name}.{name}')
        elif directory == "admin":
            return to_class(f'application.{directory}.{name}Admin.{name}Admin')
        else:
            return to_class(f'application.{directory}.{name}.{name}')

    @app.template_global()
    def get_type(value):
        return type(value).__name__

    @app.template_global()
    def titleize(name: str) -> str:
        return inflection.titleize(name)

    @app.template_global()
    def pluralize(name: str) -> str:
        return inflection.pluralize(name)

    @app.template_global()
    def singularize(name: str) -> str:
        return inflection.singularize(name)

    @app.template_global()
    def humanize(name: str) -> str:
        return inflection.humanize(name)

    @app.template_global()
    def markup(html):
        return markupsafe.Markup(html)

    @app.template_global()
    def find_key_in_dict(list_of_dicts, key, value):
        for item in list_of_dicts:
            if item[key] == value:
                return item

    @app.template_global()
    def currency_fmt(fmt, value):
        from currencies import Currency
        currency = Currency(fmt.upper())
        return currency.get_money_format(value)

    @app.template_global()
    def datetime_fmt(fmt_in, fmt_out, value):
        return datetime.datetime.strptime(value, fmt_in).strftime(fmt_out)

    @app.template_global()
    def limit_words(limit, value):
        import re
        words = re.findall(r'\w+', value)[:limit]
        limited_value = " ".join(words)
        return limited_value

    @app.template_global()
    def get_file_internal(directory, image):
        from flask import send_from_directory
        import base64
        try:
            response = send_from_directory(directory, image, as_attachment=False)
            with open(f"{directory}/{image}", "rb") as f:
                extracted_bytes = f.read()
            uri = (
                f"data:{response.headers['Content-Type']};base64,{base64.b64encode(extracted_bytes).decode('utf-8')}")
            return uri
        except werkzeug.exceptions.NotFound:
            return None

    @app.template_global()
    def render_dynamic_html(html, **kwargs):
        from packages.experimental.Hubi.Hubi import render
        return render(html, with_layout=False, **inspect.stack()[0][0].f_locals['kwargs'])

    @app.cli.command("create-resource")
    @click.argument("resource")
    def create_resource(resource: str):
        resource = inflection.singularize(resource).title()
        from string import Template
        create_view = Template(open("packages/experimental/hubi_admin/stubs/create-view.stub", "r").read()).substitute(
            Resource=resource)
        edit_view = Template(open("packages/experimental/hubi_admin/stubs/edit-view.stub", "r").read()).substitute(
            Resource=resource)
        preview_view = Template(
            open("packages/experimental/hubi_admin/stubs/preview-view.stub", "r").read()).substitute(
            Resource=resource)
        list_view = Template(open("packages/experimental/hubi_admin/stubs/list-view.stub", "r").read()).substitute(
            Resource=resource)
        submit_create = Template(
            open("packages/experimental/hubi_admin/stubs/submit-create.stub", "r").read()).substitute(
            Resource=resource)
        submit_edit = Template(open("packages/experimental/hubi_admin/stubs/submit-edit.stub", "r").read()).substitute(
            Resource=resource)
        submit_delete = Template(
            open("packages/experimental/hubi_admin/stubs/submit-delete.stub", "r").read()).substitute(
            Resource=resource)
        resource_admin = Template(
            open("packages/experimental/hubi_admin/stubs/resource-admin.stub", "r").read()).substitute(
            Resource=resource, ResourceAdmin=resource + "Admin")
        resource_model = Template(
            open("packages/experimental/hubi_admin/stubs/resource-model.stub", "r").read()).substitute(
            Resource=resource, ResourceAdmin=resource + "Admin")
        migration_file = open("packages/experimental/hubi_admin/stubs/migration.stub", "r").read().replace(
            "__MIGRATION_NAME__", f"Create{inflection.pluralize(resource)}Migration").replace(
            "__ResourceLower__", inflection.pluralize(resource).lower()
        )

        project_dir = os.getcwd()
        admin_pages_dir = os.path.join(os.getcwd(), "pages", "admin")
        models_dir = os.path.join(os.getcwd(), "application", "models")
        admin_dir = os.path.join(os.getcwd(), "application", "admin")
        migration_dir = os.path.join(os.getcwd(), "databases", "migrations")

        new_resource_dir = os.path.join(admin_pages_dir, inflection.pluralize(resource).lower())
        try:
            os.mkdir(new_resource_dir)
        except FileExistsError:
            print("Directory already exists")

        create_view_path = os.path.join(new_resource_dir, "create-" + resource.lower() + ".py")
        edit_view_path = os.path.join(new_resource_dir, "[id]" + ".py")
        preview_view_path = os.path.join(new_resource_dir, "[id]~preview" + ".py")
        list_view_path = os.path.join(new_resource_dir, "index" + ".py")
        submit_create_path = os.path.join(new_resource_dir, "create-" + resource.lower() + "(post)" + ".py")
        submit_edit_path = os.path.join(new_resource_dir, "[id]" + "(post)" + ".py")
        submit_delete_path = os.path.join(new_resource_dir, "[id]" + "delete" + ".py")

        resource_admin_path = os.path.join(admin_dir, resource + "Admin.py")
        resource_model_path = os.path.join(models_dir, resource + ".py")

        paths_to_create = [
            {"path": create_view_path, "content": create_view},
            {"path": edit_view_path, "content": edit_view},
            {"path": preview_view_path, "content": preview_view},
            {"path": list_view_path, "content": list_view},
            {"path": submit_create_path, "content": submit_create},
            {"path": submit_edit_path, "content": submit_edit},
            {"path": submit_delete_path, "content": submit_delete},
            {"path": resource_admin_path, "content": resource_admin},
            {"path": resource_model_path, "content": resource_model},
        ]

        for path in paths_to_create:
            if not os.path.exists(path["path"]):
                open(path["path"], "w").write(path["content"])
            else:
                print(f"File {path['path']} already exists")

        dt_obj_str = str(datetime.datetime.now()).replace("-", "_")
        date = dt_obj_str.split(" ")[0]
        time = dt_obj_str.split(" ")[1].split(".")[0].replace(":", "")

        os.system(
            f"masonite-orm migration create_{inflection.pluralize(resource).lower()}_table --create {inflection.pluralize(resource).lower()}")

        print("Successfully created resource " + resource + "!")
        print("The following files were created:")
        print(f""
              f"{list_view_path}\n"
              f"{edit_view_path}\n"
              f"{preview_view_path}\n"
              f"{submit_edit_path}\n"
              f"{create_view_path}\n"
              f"{submit_create_path}\n"
              f"{resource_model_path}\n"
              f"{resource_admin_path}\n")

    @app.cli.command("migration")
    @click.argument("migration")
    def migration(migration: str):
        os.system(f"masonite-orm migration {migration}")

    @app.cli.command("migrate")
    def migrate():
        os.system(f"masonite-orm migrate")

    @app.cli.command("seed")
    def seed():
        os.system(f"masonite-orm seed")

    @app.cli.command("rollback")
    def rollback():
        os.system(f"masonite-orm rollback")

    @app.cli.command("refresh")
    def refresh():
        os.system(f"masonite-orm refresh")

    @app.cli.command("reset")
    def reset():
        os.system(f"masonite-orm reset")
