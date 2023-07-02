from flask import request


class ResourcefulTrait:
    ...

    @classmethod
    def handle(cls):
        if request.method == "GET":
            if not id:
                return cls.index()
        if request.method == "POST":
            return cls.create()
        if request.method == "GET" and id:
            return cls.view(id)
        if request.method == "POST" and id:
            return cls.edit(id)

    @staticmethod
    def index():
        pass

    @staticmethod
    def create():
        pass

    @staticmethod
    def view(id):
        pass

    @staticmethod
    def edit(id):
        pass
