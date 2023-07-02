from . import Checkbox

class Toggle(Checkbox):
    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({
            "type": "toggle",
            "checked_color": "primary",
        })




