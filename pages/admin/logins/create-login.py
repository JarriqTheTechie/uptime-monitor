from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="Create Login")
def home():
    admin = Admin()
    html = admin.setup_create_view("Login")
    return html
