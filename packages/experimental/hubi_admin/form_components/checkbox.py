from .field import Field


class Checkbox(Field):
    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "checkbox", "checked_color": "primary"})

    def checked(self):
        self.field_data.update({"checked": "true"})
        return self

    def inline(self):
        self.field_data.update({"inline": True})
        return self

    def checked_color(self, color: str):
        self.field_data.update({"checked_color": f"{color}"})
        return self



