from packages.experimental.Hubi.Hubi import render
from packages.stable.flask_fs_router import endpoint


@endpoint(name="Welcome Page")
def home():
    # language=HTML
    return render(
        """
            {{ liveflask('NoticeComponent')|safe }}
            <h1>{{ page_title }}</h1>
        """, with_layout=True
    )
