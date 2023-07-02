import glob
import inspect
import json
import os
import pprint

import flask
import inflection
from flask import abort, redirect, render_template, request, url_for
from masoniteorm.collection import Collection
from werkzeug.datastructures.file_storage import FileStorage
from helpers import to_class
from helpers import getByDot
from packages.experimental.Hubi.Hubi import render
from packages.stable.flask_requester.flask_requester import requester
import urllib.parse


class Admin:
    def __init__(self):
        self.admin_object = {}
        self.models = []

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.admin_object.update({"name": name})
        return obj

    def view(self, view: str):
        self.admin_object.update({"view": view})
        return self

    def build_guards(self, model):
        available_guard_methods = [
            "can_list", "can_view", "can_create", "can_edit", "can_delete", "can_export", "can_import", "can_filter"
        ]
        declared_guards = []

        for method in available_guard_methods:
            if hasattr(model(), method):
                declared_guards.append(method)

        can_list = model().can_list() if "can_list" in declared_guards else True
        can_view = model().can_view() if "can_view" in declared_guards else True
        can_create = model().can_create() if "can_create" in declared_guards else True
        can_edit = model().can_edit() if "can_edit" in declared_guards else True
        can_delete = model().can_delete() if "can_delete" in declared_guards else True
        can_export = model().can_export() if "can_export" in declared_guards else True
        can_import = model().can_import() if "can_import" in declared_guards else True
        can_filter = model().can_filter() if "can_filter" in declared_guards else True

        return {
            "can_list": True if can_list is None else can_list,
            "can_view": True if can_view is None else can_view,
            "can_create": True if can_create is None else can_create,
            "can_edit": True if can_edit is None else can_edit,
            "can_delete": True if can_delete is None else can_delete,
            "can_export": True if can_export is None else can_export,
            "can_import": True if can_import is None else can_import,
            "can_filter": True if can_filter is None else can_filter,
        }

    def compile(self, resource, result_set=None):
        import urllib.parse
        model = to_class(f'application.models.{resource}.{resource}')
        models = self.__generate_models__()


        model_label = getattr(model, "get_model_label", getattr(model, "model_label", resource))


        admin_model_dict = {
            "resource": [
                {
                    "name": resource,
                    "model_label": model_label,
                    "resource_name_mutations": {
                        "singular": inflection.singularize(resource),
                        "plural": inflection.pluralize(resource),
                    },
                    "model": model,
                    "schema": {
                        "table": model().get_table_columns(),
                        "form": model().get_fillable(),
                    },
                    "pagination": {
                        "per_page": requester.input("per_page", 10),
                        "page": requester.input("page", 1),
                    },
                    "filters": {
                        "default": model.__admin_list_filter__,
                        "request_filter": requester.input('filter', 'asc'),
                    },
                    "search": {
                        "search_field": model.__admin_search_field__,
                        "search_query": requester.input('search', '%'),
                    },
                    "query_params_string": f"/admin/{inflection.pluralize(resource).lower()}?" + urllib.parse.urlencode(
                        {
                            "filter": requester.input('filter', 'asc'),
                            "per_page": requester.input("per_page", 10),
                            "page": requester.input("page", 1),
                            "search_query": requester.input('search', '%'),
                        }),
                    "permissions": self.build_guards(model),
                }
            ],
            "models": models,
        }
        search_field = admin_model_dict["resource"][0]["search"]["search_field"]
        search_query = admin_model_dict["resource"][0]["search"]["search_query"]
        per_page = admin_model_dict["resource"][0]["pagination"]["per_page"]
        page = admin_model_dict["resource"][0]["pagination"]["page"]
        filters = admin_model_dict["resource"][0]["filters"]["default"]
        request_filters = admin_model_dict["resource"][0]["filters"]["request_filter"]

        def process_result_set(result_set=None):

            if result_set is None:
                result_set = model()

            def build_search_query(q):
                if isinstance(search_field, list):
                    for i, field in enumerate(search_field):
                        if i == 0:
                            if "." in field:
                                result_set = q.where_has(
                                    f"{field.split('.')[0]}",
                                    lambda q: q.where(field.split('.')[1], "like", f"%{search_query.strip()}%")
                                )
                            else:
                                result_set = q.where(field, "like", f"%{search_query.strip()}%")
                        else:
                            if "." in field:
                                result_set = q.or_where_has(
                                    f"{field.split('.')[0]}",
                                    lambda q: q.where(field.split('.')[1], "like", f"%{search_query.strip()}%")
                                )
                            else:
                                result_set = q.or_where(field, "like", f"%{search_query.strip()}%")
                else:
                    if "." in search_field:
                        result_set = q.where_has(
                            f"{search_field.split('.')[0]}",
                            lambda q: q.where(field.split('.')[1], "like", f"%{search_query.strip()}%")
                        )
                    else:
                        result_set = q.where(search_field, "like", f"%{search_query.strip()}%")
                return result_set

            result_set = result_set.where(
                lambda q: build_search_query(q)
            )

            result_set = result_set.order_by(filters, request_filters).paginate(int(requester.input("per_page", 10)),                                                             int(requester.input("page", 1)))
            return result_set

        result_set = process_result_set(result_set)
        admin_model_dict["resource"][0].update({"result_set": result_set or {}})
        return admin_model_dict

    def setup_list_view(self, resource: str, result_set=None):
        view_mode = "list"
        page_title = f"{inflection.pluralize(resource).title()}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        import timeit
        start_time = timeit.default_timer()
        data_model = self.compile(resource, result_set)
        if data_model["resource"][0]["permissions"]["can_list"] is False:
            return abort(403)

        resource = data_model["resource"][0]["name"]
        model = data_model["resource"][0]["model"]
        result_set = data_model["resource"][0]["result_set"]
        fields = data_model["resource"][0]["schema"]["table"]
        pagination = data_model["resource"][0]["pagination"]
        query_param_string = data_model["resource"][0]["query_params_string"]
        elapsed = timeit.default_timer() - start_time
        print(f"Time elapsed: {elapsed}")

        try:
            header_metrics = model().get_header_metrics()
        except AttributeError:
            header_metrics = None

        try:
            table_filters = model().get_table_filters()
        except AttributeError:
            table_filters = None

        try:
            table_actions = model().get_table_actions()
        except AttributeError:
            table_actions = None
        # language=HTML
        if 'hx' not in request.args:
            return render_template("admin/views/ListView.html", **locals())
        else:
            resp = flask.make_response(
                render_template("admin/views/ListView.html", **locals())
            )
            resp.headers['HX-Redirect'] = request.path
            return resp

    def setup_create_view(self, resource: str):
        view_mode = "create"
        data_model = self.compile(resource)
        page_title = f"Create {inflection.singularize(getByDot(data_model['resource'][0], 'model_label')).title()}"
        if data_model["resource"][0]["permissions"]["can_create"] is False:
            return abort(403)
        submit_url = f"/admin/{getByDot(data_model['resource'][0], 'resource_name_mutations.plural').lower()}/create-{getByDot(data_model['resource'][0], 'resource_name_mutations.singular').lower()}"
        query_param_string = getByDot(data_model['resource'][0], 'query_param_string')
        result_set = {}
        fields = data_model["resource"][0]['schema']['form']
        # language=HTML
        return render_template("admin/views/CreateView.html", **locals())

    def setup_edit_view(self, resource: str, id: int, result_set=None):
        view_mode = "edit"
        page_title = f"Edit {inflection.singularize(resource).title()}"
        data_model = self.compile(resource, result_set)
        model = data_model['resource'][0]['model']
        fields = data_model['resource'][0]['schema']['form']
        if data_model["resource"][0]["permissions"]["can_edit"] is False:
            return abort(403)
        try:
            edit_actions = model().admin_actions()
        except AttributeError:
            edit_actions = None

        try:
            relations = model().get_relations()
        except AttributeError:
            relations = None

        submit_url = f"/admin/{inflection.pluralize(resource).lower()}/{id}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        result_set = model.find(id)
        if not result_set:
            return abort(404)

        models = data_model['models']

        # language=HTML
        return render_template("admin/views/EditView.html", **locals())

    def setup_preview_view(self, resource: str, id: int, result_set=None):
        view_mode = "preview"
        page_title = f"Preview {inflection.singularize(resource).title()}"
        data_model = self.compile(resource, result_set)
        model = data_model['resource'][0]['model']
        if data_model["resource"][0]["permissions"]["can_view"] is False:
            return abort(403)
        try:
            edit_actions = model().admin_actions()
        except AttributeError:
            edit_actions = None

        try:
            relations = model().get_relations()
        except AttributeError:
            relations = None

        submit_url = f"/admin/{inflection.pluralize(resource).lower()}/{id}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        result_set = model.find(id)
        fields = data_model['resource'][0]['schema']['form']
        # language=HTML
        return render_template("admin/views/PreviewView.html", **locals())

    def submit_edit_view(self, resource: str, id: int, data):
        resoure_pluralized = inflection.pluralize(resource).lower()
        resoure_singularized = inflection.singularize(resource).lower()
        redirect_url = f"/admin/{resoure_pluralized}"
        model = to_class(f'application.models.{resource}.{resource}')
        data_model = self.compile(resource)
        if data_model["resource"][0]["permissions"]["can_edit"] is False:
            return abort(403)
        try:
            fields = model.__admin_editable__
        except AttributeError:
            fields = model().get_fillable()

        save_action = data.get('save-action')
        if save_action == "Save Changes":
            redirect_url = f"/admin/{resoure_pluralized}"
        elif save_action == "Save & Continue Editing":
            redirect_url = f"/admin/{resoure_pluralized}/{id}"
        del data['save-action']

        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame

        result_set = model.find(id)
        for key in list(data):
            if type(data[key]).__name__ == FileStorage.__name__:
                del data[key]
                data[key] = requester.store(key)
        if getattr(model, "before_edit", None):
            data = getattr(model(), "before_edit")(data)
        result_set.update(data)
        if getattr(model, "after_edit", None):
            result_set = getattr(model(), "after_edit")(result_set)

        if save_action == "Save Changes":
            redirect_url = f"{redirect_url}?hx=true"
            return redirect(redirect_url)
        elif save_action == "Save & Continue Editing":
            redirect_url = f"/admin/{resoure_pluralized}/{id}"
            return redirect(redirect_url)

    def submit_create_view(self, resource: str, data, redirect_to_new=True):
        data_model = self.compile(resource)
        model = to_class(f'application.models.{resource}.{resource}')
        if data_model["resource"][0]["permissions"]["can_create"] is False:
            return abort(403)
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame

        save_action = data.get('save-action')
        del data['save-action']

        redirect_url = None
        for key in list(data):
            if type(data[key]).__name__ == FileStorage.__name__:
                del data[key]
                data[key] = requester.store(key)
            if key == "redirect_url":
                redirect_url = data[key]
                del data[key]

        if getattr(model, "before_create", None):
            data = getattr(model(), "before_create")(data)
        new_model = model.create(data)
        if getattr(model, "after_create", None):
            new_model = getattr(model(), "after_create")(new_model)

        if save_action == "Save & Create New":
            redirect_url = f"/admin/{inflection.pluralize(resource).lower()}/create-{inflection.singularize(resource).lower()}"
        if save_action == "Save":
            redirect_url = f"/admin/{inflection.pluralize(resource).lower()}"

        if save_action == "Save":
            if redirect_to_new:
                return redirect(f"/admin/{inflection.pluralize(resource).lower()}/{new_model.id}")
            else:
                return redirect(redirect_url)
        elif save_action == "Save & Create New":
            return redirect(redirect_url)

    def delete_view(self, resource: str, id: int):
        resoure_pluralized = inflection.pluralize(resource).lower()
        resoure_singularized = inflection.singularize(resource).lower()
        model = to_class(f'application.models.{resource}.{resource}')
        submit_url = f"/admin/{resoure_pluralized}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        result_set = model.find(id)
        result_set.delete()
        return "", 200

    def __generate_models__(self):
        for file in glob.glob("application/models" + "/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if name == "__init__":
                continue
            else:
                model = to_class("application.admin." + name + "Admin." + name + "Admin")
                display_in_nav = True
                try:
                    if type(model.display_in_nav) == bool:
                        display_in_nav = model.display_in_nav
                except AttributeError:
                    display_in_nav = True
                if display_in_nav:
                    self.models.append({
                        "name": name,
                        "class": model,
                        "label": getattr(model(), "navigation_label", None),
                    })
        return self.models

    def __register_model__(self, model: str):
        model = {
            "name": model,
            "class": to_class("application.models." + model + "." + model),
        }
        self.models.append(model)
        return self

    def __deregiseter_model__(self, model: str):
        self.models = [m for m in self.models if m["name"] != model]
        return self
