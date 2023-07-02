from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="Preview User")
def home(id):
    admin = Admin()
    html = admin.setup_preview_view("User", id)
    return html
