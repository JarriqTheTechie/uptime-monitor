from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint
from packages.stable.flask_requester.flask_requester import requester


@endpoint(name="Create Login POST")
def home():
    data = requester.all()
    admin = Admin()
    return admin.submit_create_view("Login", data)
