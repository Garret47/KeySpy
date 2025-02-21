from typing import Type

from .registers import Register
from .styles import WidgetStyle


class Director:
    @staticmethod
    def render(register: Type[Register], style: WidgetStyle):
        builder = register.get_builder(style)(style)
        for child in getattr(style, 'children', []):
            Director.render(register, child)
        builder.run()
