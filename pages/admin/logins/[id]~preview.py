from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="Preview Login")
def home(id):
    admin = Admin()
    html = admin.setup_preview_view("Login", id)
    return html
