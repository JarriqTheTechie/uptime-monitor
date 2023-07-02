from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint
from packages.stable.flask_requester.flask_requester import requester


@endpoint(name="Edit User POST")
def home(id):
    data = requester.all()
    admin = Admin()
    return admin.submit_edit_view("User", id, data)
