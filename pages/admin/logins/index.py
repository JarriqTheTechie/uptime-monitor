from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="Login")
def home():
    admin = Admin()
    html = admin.setup_list_view("Login")
    return html

