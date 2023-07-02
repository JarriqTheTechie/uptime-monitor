from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="User")
def home():
    admin = Admin()
    html = admin.setup_list_view("User")
    return html

