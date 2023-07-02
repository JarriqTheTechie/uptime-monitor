"""
@app.template_global()
        def google_drive_cdn(url):
            return GoogleAsCDN(url).link()
"""


class GoogleAsCDN:
    def __init__(self, url):
        self.url: str = url

    def link(self) -> str:
        file_id: str = self.url.split("d/")[1].split("/view")[0]
        link: str = f"https://drive.google.com/uc?export=view&id={file_id}"
        return link