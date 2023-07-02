import json
import pprint
from typing import Dict, Any, Optional

from MVLive import MVLive
from flask import request, Response

from packages.stable.flask_fs_router import endpoint


@endpoint(name="mv_live")
def default() -> Response:
    req = request.json
    _class: object = MVLive().from_snapshot(req)

    if hasattr(_class, 'boot' ):
        _class.boot()

    if hasattr(_class, 'booted' ):
        _class.booted()


    if req.get('method'):
        method = req.get('method')
        args = req.get('args')
        if method != "emit":
            MVLive().call_method(_class, method, *tuple(args.split(",")))
        else:
            MVLive().call_event_handler(_class, method, args)
    if req.get('update_property'):
        if hasattr(_class, 'updating'):
            _class.updating()
        req_updated_prop = req.get('update_property')
        MVLive().update_property(_class, req_updated_prop[0], req_updated_prop[1])
    html, snapshot = MVLive().to_snapshot(_class, req['snapshot']['key'])
    return {
        "html": html, "snapshot": snapshot
    }