from packages.stable.ad_auth import ad_auth
from packages.stable.flask_fs_router import endpoint
from packages.stable.flask_requester.flask_requester import requester


@endpoint(name="login post")
def home():
    username, password = requester.input("username"), requester.input("password")
    return ad_auth(username, password, '/admin')
