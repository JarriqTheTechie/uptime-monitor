from . import TextInput

class FileUpload(TextInput):
    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "file"})

    def multiple(self):
        self.field_data.update({"multiple": "true"})
        return self

