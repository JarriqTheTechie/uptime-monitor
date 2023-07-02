import pprint
import secrets
from pathlib import Path
from pydoc import locate
from typing import Any
from functools import wraps


def to_class(path: str) -> Any:
    """
        Converts string class path to a python class

    return:
        mixed
    """
    try:
        class_instance = locate(path)
    except ImportError:
        class_instance = None
    return class_instance or None


class FlaskFSRouter:
    def __init__(self, app=None):
        self.possible_routes = []
        self.fqdns = []
        self.route_paths = []
        self.route_map = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        [
            app.add_url_rule(
                route.get('path'),
                **dict(
                    view_func=route.get('view_func'),
                    endpoint=route.get('endpoint'),
                    methods=[route.get('method')],
                    websocket=route.get("ws")
                )
            ) for route in FlaskFSRouter().routes_export()
        ]

    def find_routes_files(self):

        pages_path = Path('pages')
        pages = list(pages_path.glob('**/*.py'))
        [
            self.possible_routes.append(
                str(page).lstrip("pages").lstrip("\\").replace("\\", "."))
            for page in pages
        ]
        return self

    def generate_fqdns(self):
        import inspect
        import importlib

        for my_module in self.possible_routes:
            my_module_str = f"pages.{my_module.rstrip('.py')}"
            my_module = importlib.import_module(my_module_str)
            my_module_functions = [f for f in vars(my_module).values() if inspect.isfunction(f)]
            for fn in my_module_functions:
                if hasattr(fn, "__is_endpoint__"):
                    self.fqdns.append(f"{my_module_str}.{fn.__name__}")
        return self

    def fqdns_to_route_path(self):
        for path in self.fqdns:
            fqdn = path
            path = path.replace("pages.", "/").replace(".", "/").replace("index/", "").replace(
                "[", "<").replace("]", ">").replace("/index", "").replace("~", "/")

            split_path = path.split(">")
            end_of_arg_position = path.split(">")[0].__len__()
            try:
                if path[end_of_arg_position+1] != "/":
                    path = f"{path[:end_of_arg_position]}>/{split_path[1]}"
            except IndexError:
                pass

            method = fqdn.split("(")[-1].split(')')[0]
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                method = method
            else:
                method = "GET"

            if path == "/":
                pass
            else:
                path = path.rstrip("/")

            fqdn = fqdn.replace("//", '').replace("/", '.').replace("..", '.')
            path = path.replace(f'({method})', '').replace("//", '/') or '/'
            self.route_map.append({
                "path": ["/" if path.rstrip(f"{fqdn.split('.')[-1]}").rstrip("/") == "" else path.rstrip(f"{fqdn.split('.')[-1]}").rstrip("/")][0],
                "fqdn": fqdn,
                "view_func": to_class(fqdn),
                "endpoint": to_class(fqdn).__endpoint_name__,
                "method": method,
                "ws": to_class(fqdn.replace(f"{fqdn.split('.')[-1]}", "ws")) or False
            })
        return self

    def routes_export(self):
        return self.find_routes_files().generate_fqdns().fqdns_to_route_path().route_map


def endpoint(func_=None, name:str=""):

    def _decorator(func):
        func.__is_endpoint__ = True
        func.__endpoint_name__ = name
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("calling decorated function")
            return func(*args, **kwargs)
        return wrapper

    if callable(func_):
        return _decorator(func_)
    elif func_ is None:
        return _decorator
    else:
        raise ValueError("Positional arguments are not supported.")
