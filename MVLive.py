import json
import pprint
import secrets
from pydoc import locate
from typing import Any
import functools

from flask import render_template_string
from masoniteorm.collection import Collection
import hashlib


def set_attribute(obj, path_string, new_value):
    parts = path_string.split('.')
    final_attribute_index = len(parts)-1
    current_attribute = obj
    i = 0
    for part in parts:
        new_attr = getattr(current_attribute, part, None)
        if current_attribute is None:
            print('Error %s not found in %s' % (part, current_attribute))
            break
        if i == final_attribute_index:
            setattr(current_attribute, part, new_value)
        current_attribute = new_attr
        i+=1


def get_attribute(obj, path_string):
    parts = path_string.split('.')
    final_attribute_index = len(parts)-1
    current_attribute = obj
    i = 0
    for part in parts:
        new_attr = getattr(current_attribute, part, None)
        if current_attribute is None:
            print('Error %s not found in %s' % (part, current_attribute))
            return None
        if i == final_attribute_index:
            return getattr(current_attribute, part)
        current_attribute = new_attr
        i += 1


def to_class(path: str) -> Any:
    """
        Converts string class path to a python class

    return:
        mixed
    """
    try:
        class_instance = locate(path)
    except ImportError:
        print('Module does not exist')
    return class_instance or None


class MVLive:
    def inital_render(self, _class, key=""):

        _class = to_class(f"templates.components.mvlive.{_class}.{_class}")
        component_name = _class.__name__

        if hasattr(_class, 'boot'):
            _class().boot()

        if hasattr(_class, 'mount'):
            _class().mount()

        if hasattr(_class, 'booted'):
            _class().booted()

        set_attribute(_class, 'key', key)
        html, snapshot = self.to_snapshot(_class(), key)
        snapshot_attr = json.dumps(snapshot)
        return render_template_string(
            """
                <div data-component="{{ component_name }}" id="{{ key }}" data-snapshot="{{ snapshot_attr }}">
                    {{html|safe}}
                </div>
            """, snapshot_attr=snapshot_attr, html=html, key=key, component_name=component_name
        )

    def get_props(self, component):
        props = {}
        method_list = [attribute for attribute in dir(component) if callable(getattr(component, attribute)) and attribute.startswith('__') is False]

        for key in component.__dict__.items():
            if key[0].startswith("_"):
                continue
            if key[0] in method_list:
                continue
            else:
                props[f'{key[0]}'] = key[1]
        return props

    def from_snapshot(self, req_snapshot):

        req_checksum = req_snapshot['snapshot']['checksum']
        del req_snapshot['snapshot']['checksum']
        if 'children' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['children']
        if 'models' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['models']
        if 'actions' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['actions']
        if 'polls' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['polls']
        pprint.pprint(req_snapshot['snapshot'])
        source_checksum = hashlib.md5(json.dumps(req_snapshot['snapshot'], sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()



        if source_checksum != req_checksum:
            raise Exception("Stop trying to hack me.")

        _class = req_snapshot['snapshot']['class']
        data = req_snapshot['snapshot']['data']
        #children = req_snapshot['snapshot']['children']
        _class = to_class(f"templates.components.mvlive.{_class}.{_class}")()
        for prop in data.items():
            setattr(_class, prop[0], prop[1])
        return _class


    def call_method(self, component, method, *args):
        if "__NOVAL__" in args:
            args = ()
        else:
            args = [json.loads(x) for x in args]
        return getattr(component, method)(*args)


    def call_event_handler(self, _class, parsed_method, param):
        props = self.get_props(_class)
        #print( _class, parsed_method, json.loads(param))
        args_list = [json.loads(x) for x in param.split(",")]
        if 'listeners' in props:
            event = args_list[0]
            args_list.pop(0)
            print(args_list)
            if args_list[0] != "__NOVAL__":
                getattr(_class, props['listeners'][event])(*tuple(args_list))
            else:
                getattr(_class, props['listeners'][event])()


    def to_snapshot(self, _class, key):
        props = self.get_props(_class)
        html = render_template_string(
            _class.render(),
            **props
        )


        #meta = self.dehydrate_properties(props)

        snapshot = {
            "class": _class.__class__.__name__,
            "key": key,
            "data": props,
            #"html": html,
        }
        snapshot['checksum'] = hashlib.md5(json.dumps(snapshot, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()


        return html, snapshot


    def access_nested_dict_in_component(self, _class, prop, val):
        props = self.get_props(_class)
        for key in props.keys():
            if key == prop.split('.')[0]:
                _class.__dict__[key][prop.split('.')[1]] = val


    def update_property(self, _class, prop, val):
        if "." in prop:
            self.access_nested_dict_in_component(_class, prop, val)
        else:
            setattr(_class, prop, val)
        updated_hook = f'updated{prop.split(".")[0].title()}'
        updating_hook = f'updating{prop.title()}'
        if hasattr(_class, 'updated'):
            _class.updated()
        if hasattr(_class, updated_hook):
            getattr(_class, updated_hook)()


    def dehydrate_properties(self, props):
        data = {}
        meta = {}

        for key in props.items():
            if isinstance(key[1], Collection):
                value = key[1].to_dict()
                meta[key[0]] = 'collection'
                data[key[1]] = value
            else:
                pass
        return data, meta

