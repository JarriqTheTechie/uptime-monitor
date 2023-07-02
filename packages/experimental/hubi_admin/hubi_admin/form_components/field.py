class Field:
    def __init__(self):
        self.field_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.field_data.update({"name": name})
        return obj

    def class_list(self, classes: list):
        self.field_data.update({"classes": " ".join(classes)})
        return self


    def id(self, id: str):
        self.field_data.update({"id": id})
        return self

    
    def label(self, label: str):
        self.field_data.update({"label": label})
        return self

    
    def required(self):
        self.field_data.update({"required": "true"})
        return self

    
    def disabled(self):
        self.field_data.update({"disabled": "true"})
        return self

    
    def readonly(self):
        self.field_data.update({"readonly": "true"})
        return self

    
    def autofocus(self):
        self.field_data.update({"autofocus": "true"})
        return self

    def colspan(self, span: str):
        self.field_data.update({"colspan": f"{span}"})
        return self

    
    def render(self):
        return self.field_data