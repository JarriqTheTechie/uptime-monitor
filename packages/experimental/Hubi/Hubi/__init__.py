import inspect
import os
import pprint

import markupsafe
from packages.stable.flask_fs_router import FlaskFSRouter
from flask import render_template_string, request, render_template
from packages.experimental.mv_components.mv_components import render_inline, MVComponent
from packages.HubiWire import HubiWire


def show_callers_locals():
    """Print the local variables in the caller's frame."""
    import inspect
    frame = inspect.currentframe()
    try:
        pass
    finally:
        del frame


def render(html: str, with_layout: bool = True, is_path=False, **kwargs) -> str:
    """

    :rtype: object
    """
    from flask import current_app
    from string import Template
    application_name = current_app.config.get('ApplicationName') or "SAAS Application Template"
    try:
        page_title = inspect.stack()[2][0].f_locals.get("func").__dict__.get("__endpoint_name__").title()
    except AttributeError:
        try:
            page_title = inspect.stack()[3][0].f_locals.get("func").__dict__.get("__endpoint_name__").title()
        except AttributeError:
            page_title = "Page Title"
    this_caller = inspect.stack()[0][0].f_locals
        #this_caller.update(kwargs)
    for key in ["html", "with_layout", "current_app", "caller", "Template"]:
        if this_caller.get(key):
            del this_caller[key]
    caller = inspect.stack()[1][0]
    myvars = caller.f_locals
    myvars = {**this_caller, **myvars}
    if kwargs:
        myvars.update(kwargs)
    html, output = html, html
    if with_layout:
        return render_template("components/layouts/BaseLayoutAdmin.html", **myvars)
    if is_path is True and with_layout is False:
        html = load_html_from_disk(html)
        return render_template_string(html, **myvars)
    return render_template_string(html, **myvars)


def load_html_from_disk(name: str) -> str:
    """
        Load html from disk.

    return:
        str
    """
    calling_python_file = os.path.abspath((inspect.stack()[1])[1])
    calling_dir = os.path.dirname(calling_python_file)
    if not os.path.exists(f"{calling_dir}\\{name}.html"):
        calling_python_file = os.path.abspath((inspect.stack()[2])[1])
        calling_dir = os.path.dirname(calling_python_file)
    calling_dir = os.path.dirname(calling_python_file)
    with open(f"{calling_dir}\\{name}.html") as f:
        return markupsafe.Markup(f.read())




class Hubi:
    def __init__(self, app=None, dir=None, Title=""):
        """

        :rtype: object
        """
        if dir:
            app.config['HubiPath'] = dir
        else:
            app.config['HubiPath'] = ["pages.hubiwire"]
        self.Title = Title
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        FlaskFSRouter(app)
        MVComponent(app)

        @app.template_global()
        def hubiwire(component, key=""):
            return render_inline("""
                {{ hubiwire|safe }}
            """, hubiwire=HubiWire().inital_render(component, key))

        @app.route("/mlive", methods=['POST'])
        def mv_live():
            req = request.json
            _class: object = HubiWire().from_snapshot(req)

            if hasattr(_class, 'boot'):
                _class.boot()

            if hasattr(_class, 'booted'):
                _class.booted()

            if req.get('method'):
                method = req.get('method')
                args = req.get('args')
                if method != "emit":
                    HubiWire().call_method(_class, method, *tuple(args.split(",")))
                else:
                    HubiWire().call_event_handler(_class, method, args)
            if req.get('update_property'):
                if hasattr(_class, 'updating'):
                    _class.updating()
                req_updated_prop = req.get('update_property')
                HubiWire().update_property(_class, req_updated_prop[0], req_updated_prop[1])
            html, snapshot = HubiWire().to_snapshot(_class, req['snapshot']['key'])
            return {
                "html": html, "snapshot": snapshot
            }
