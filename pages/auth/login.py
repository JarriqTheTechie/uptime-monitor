from packages.experimental.Hubi.Hubi import render, load_html_from_disk
from packages.stable.flask_fs_router import endpoint


@endpoint(name="login")
def home():
    # language=HTML
    return render("login", with_layout=False, is_path=True)
