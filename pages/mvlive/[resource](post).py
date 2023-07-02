import json
import pprint
from typing import Dict, Any, Optional

from MVLive import MVLive
from flask import request, Response, url_for, redirect

from helpers import to_class
from packages.stable.flask_fs_router import endpoint
from packages.stable.flask_requester.flask_requester import requester


@endpoint(name="mv_live_shorthand")
def default(resource) -> Response:
    _class: object = to_class(f"application.admin.{resource}Admin.{resource}Admin")
    model = to_class(f"application.models.{resource}.{resource}")
    method = requester.input('method')
    args = requester.input('args')
    data = requester.all()
    del data['method']
    del data['args']
    record = model.find(args)
    for action in _class().get_table_actions():
        if action['name'] == method:
            action['action'](record, data)
    return redirect(request.referrer)