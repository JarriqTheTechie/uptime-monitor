import json
import os.path
import secrets
from pydoc import locate
from string import Template
from flask import render_template_string
import hashlib
from flask import current_app

import re

from bs4 import BeautifulSoup


class LiveComponent:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def includes(str: str, sub: str):
    if str.find(sub) < 0:
        return False
    else:
        return True


def unique(sequence):
    result = []
    for item in sequence:
        if item not in result:
            result.append(item)
    return result


def css_isolate(css: str, html: str, is_style: bool = False, class_name: str = ""):
    css = css.replace("\n", "").replace("  ", "").replace("}", "}")
    replacement_pairs = []

    expr = re.compile(r'(.*?)\{.*?\}')

    for res in expr.findall(css):
        for tag in res.split():
            tag = tag.strip(",")
            if tag != "~" and tag != "+" and tag != ">":
                replacement_pairs.append({
                    f"{tag}": (
                        f'{tag}[data-hubi="{class_name}"]', f'data-hubi="{class_name}"'
                    )
                })

    for style in list(set(css.splitlines())):
        style = style.split("{")[0].lstrip().rstrip().strip(" ")
        if " " not in style:
            replacement_pairs.append({
                f"{style}": (
                    f'{style}[data-hubi="{class_name}"]', f'data-hubi="{class_name}"'
                )
            })
        else:
            paired_styles = style.strip(" ").split(" ")
            for paired_style in paired_styles:
                if "," not in paired_style or ">" not in paired_style:
                    replacement_pairs.append({
                        f"{paired_style}": (
                            f'{paired_style}[data-hubi="{class_name}"]', f'data-hubi="{class_name}"'
                        )
                    })
                if "," in paired_style:
                    replacement_pairs.append({
                        f"{paired_style}": (
                            f'{paired_style.strip(",")}[data-hubi="{class_name}"],', f'data-hubi="{class_name}"'
                        )
                    })
                if ">" in paired_style:
                    replacement_pairs.append({
                        f"{paired_style}": (
                            f'{paired_style.strip(">")}[data-hubi="{class_name}"] >', f'data-hubi="{class_name}"'
                        )
                    })

    replacement_tags = []

    for d in unique(replacement_pairs):
        replacement_key = list(d.keys())[0]
        if replacement_key not in [">", ","]:
            if is_style:
                if f"{replacement_key}" in html:
                    html = html.replace(
                        f"{replacement_key}",
                        f"{d[f'{replacement_key}'][0]}"
                    )

            else:
                soup = BeautifulSoup(html, 'html.parser')
                matches = soup.select(f"{replacement_key.strip(',').split(':')[0]}")
                for match in matches:
                    val: str = str(match)
                    index = val.index(" ")
                    replacement = val[:index] + f' {list(d.values())[0][1]}'
                    replacement_tags.append((
                        str(val[:index]), replacement
                    ))

            if len(replacement_tags) != 0:
                for replacement_tag in replacement_tags:
                    html = html.replace(replacement_tag[0].lstrip().rstrip(), replacement_tag[1].lstrip().rstrip())

    return html



def set_attribute(obj, path_string, new_value):
    parts = path_string.split('.')
    final_attribute_index = len(parts) - 1
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
        i += 1


def get_attribute(obj, path_string):
    parts = path_string.split('.')
    final_attribute_index = len(parts) - 1
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


def to_class(path: str):
    """
        Converts string class path to a python class

    return:
        mixed
    """
    return locate(path)

def classify(module, name):
    return type(name, (LiveComponent,), dict(module))

def find_between(s, start, end):
    return (s.split(start))[1].split(end)[0]


class HubiWire:
    def inital_render(self, _class_name, key=""):
        page_found: bool = False
        page_found_path: str = ""
        for component_path in current_app.config['HubiPath']:
            if not os.path.exists(os.path.join(component_path, _class_name + ".html")):
                continue
            else:
                page_found = True
                page_found_path = component_path
                break

        if not page_found:
            return

        source_code: Template = Template("""
from packages.Hubi import render
from LiveComponent import LiveComponent
#$IMPORTS

class $CLASS_NAME(LiveComponent):
    $BODY
    def show(self):
        return '''$HTML'''
""".strip())


        hubi_page: str = open(os.path.join(page_found_path, _class_name + ".html")).read()
        indent: str = '    '
        python_code: str = indent + find_between(hubi_page, '<python>', '</python>').replace('\n', '\n' + indent)
        html_code: str = hubi_page.split('\n</python>')[-1]
        source_code: str = source_code.safe_substitute(CLASS_NAME=_class_name, BODY=python_code, HTML=html_code)
        filename_noext = f'hubi_{secrets.token_urlsafe(24)}'.replace("-", "")
        print(filename_noext)
        with open(f'tmp/{filename_noext}.py', 'w') as f:
            f.write(source_code)

        _class = to_class(f'tmp.{filename_noext}.{_class_name}')
        _class = _class()
        print(f'temp.{filename_noext}.{_class_name}')
        os.remove(f'tmp/{filename_noext}.py')


        if hasattr(_class, 'boot'):
            _class.boot()

        if hasattr(_class, 'mount'):
            _class.mount()

        if hasattr(_class, 'booted'):
            _class.booted()

        set_attribute(_class, 'key', key)
        html, snapshot = self.to_snapshot(_class, key)
        snapshot_attr = json.dumps(snapshot)

        return render_template_string(
            """
                <div data-component="{{ component_name }}" id="{{ key }}" data-snapshot="{{ snapshot_attr }}">
                    {{html|safe}}
                </div>
            """, snapshot_attr=snapshot_attr, html=html, key=key, component_name=_class_name
        )

    @property
    def _hidden_attrs(self):
        """
        A list of meld variables and functions that are hidden from the view
        """
        return ["id", "show", "validate", "updated", "form"]

    def get_props(self, component):
        """
        Get attributes that can be called in the component.
        """
        props = {}
        attributes_names = [
            attr
            for attr in dir(component)
            if not callable(getattr(component, attr))
               and not attr.startswith("_")
               and attr not in self._hidden_attrs
        ]
        for name in attributes_names:
            props[name] = getattr(component, name)

        return props

    def from_snapshot(self, req_snapshot):
        """
        Get attributes from component snapshot
        """
        print(req_snapshot)
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
        source_checksum = hashlib.md5(
            json.dumps(req_snapshot['snapshot'], sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()

        if source_checksum != req_checksum:
            raise Exception("Stop trying to hack me.")

        _class = req_snapshot['snapshot']['class']
        data = req_snapshot['snapshot']['data']
        # children = req_snapshot['snapshot']['children']
        print(f"pages.mvlive.{_class}.{_class}")
        _class_name = req_snapshot['snapshot']['class']
        python_code_marker: str = "---"
        python_code: str = ""
        html_code: str = ""
        source_code = Template("""
from packages.Hubi import render
from LiveComponent import LiveComponent

class $CLASS_NAME(LiveComponent):
    $BODY
    def show(self):
        return '''$HTML'''
""".strip())
        page_found: bool = False
        page_found_path: str = ""
        for component_path in current_app.config['HubiPath']:
            if not os.path.exists(os.path.join(component_path, _class_name + ".html")):
                continue
            else:
                page_found = True
                page_found_path = component_path
                break

        if not page_found:
            return

        source_code: Template = Template("""
from packages.Hubi import render
from LiveComponent import LiveComponent
#$IMPORTS

class $CLASS_NAME(LiveComponent):
    $BODY
    def show(self):
        return '''$HTML'''
        """.strip())

        hubi_page: str = open(os.path.join(page_found_path, _class_name + ".html")).read()
        indent: str = '    '
        python_code: str = indent + find_between(hubi_page, '<python>', '</python>').replace('\n', '\n' + indent)
        html_code: str = hubi_page.split('\n</python>')[-1]
        source_code: str = source_code.safe_substitute(CLASS_NAME=_class_name, BODY=python_code, HTML=html_code)

        filename_noext = f'hubi_{secrets.token_urlsafe(24)}'.replace("-", "")
        print(filename_noext)
        with open(f'tmp/{filename_noext}.py', 'w') as f:
            f.write(source_code)

        _class = to_class(f'tmp.{filename_noext}.{_class_name}')
        _class = _class()
        print(f'temp.{filename_noext}.{_class_name}')
        os.remove(f'tmp/{filename_noext}.py')

        for prop in data.items():
            setattr(_class, prop[0], prop[1])
        return _class

    def call_method(self, component, method, *args):
        """
        Call method on component.
        """
        if "__NOVAL__" in args:
            args = ()
        else:
            args = [json.loads(x) for x in args]
        return getattr(component, method)(*args)

    def call_event_handler(self, _class, parsed_method, param):
        """
        Call event handler
        """
        props = self.get_props(_class)
        # print( _class, parsed_method, json.loads(param))
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
            _class.show(),
            **props
        )
        try:
            open_tag = "<style hubi='true'>"
            close_tag = '</style>'
            start = html.find(open_tag) + len(open_tag)
            end = html.find(close_tag)
            original_css = html[start:end]
            html = html.replace(open_tag + html[start:end] + close_tag,
                                open_tag + css_isolate(html[start:end], html[start:end], is_style=True,
                                                       class_name=_class.__class__.__name__) + close_tag)
            html = css_isolate(original_css, html, class_name=_class.__class__.__name__)
        except:
            pass

        # meta = self.dehydrate_properties(props)

        snapshot = {
            "class": _class.__class__.__name__,
            "key": key,
            "data": props,
            # "html": html,
        }
        snapshot['checksum'] = hashlib.md5(
            json.dumps(snapshot, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()
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

