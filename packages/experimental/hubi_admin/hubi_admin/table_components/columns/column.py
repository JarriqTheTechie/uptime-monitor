class Column:
    def __init__(self):
        self.column_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.column_data.update({"name": name})
        return obj

    def label(self, label: str):
        self.column_data.update({"label": label})
        return self

    def default(self, value: str):
        self.column_data.update({"default": value})
        return self

    def render(self):
        return self.column_data

