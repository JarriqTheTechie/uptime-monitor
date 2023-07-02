import glob
import os
from typing import List

from flask import render_template

from packages.experimental.Hubi.Hubi import render, load_html_from_disk
from packages.experimental.hubi_admin import Admin
from packages.stable.flask_fs_router import endpoint


@endpoint(name="")
def home():
    models = Admin().__generate_models__()
    # language=HTML
    return render(
        """
        <mv-layouts.BaseLayoutAdmin application_name={{ application_name }} page_title={{ page_title }} models={{ models }}>
            {{ from_config('admin') }}
        </mv-layouts.BaseLayoutAdmin>
        """, with_layout=False#, is_path=True
    )
