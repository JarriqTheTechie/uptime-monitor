from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="Create User")
def home():
    admin = Admin()
    html = admin.setup_create_view("User")
    return html
