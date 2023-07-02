class Relation:
    def __init__(self):
        self.relation_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.relation_data.update({"name": name})
        return obj

    def heading(self, heading: str):
        self.relation_data.update({"heading": heading})
        return self

    def description(self, description: str):
        self.relation_data.update({"description": description})
        return self

    def class_(self, class_name: str):
        self.relation_data.update({"class_": class_name})
        return self

    def render(self):
        return self.relation_data