from typing import Protocol
from packages.Hubi import render


class BaseComponent(Protocol):
    def __init__(self, **kwargs):
        ...

    def render(self):
        ...


