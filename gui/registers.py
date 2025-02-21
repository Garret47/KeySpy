from typing import Type

from .styles import WidgetStyle
from .builders import InterfaceBuilder


class Register:
    _registry: dict = {}

    @classmethod
    def registry(cls, style_cls: Type[WidgetStyle], builder_cls: Type[InterfaceBuilder]):
        cls._registry[style_cls] = builder_cls

    @classmethod
    def get_builder(cls, style: WidgetStyle):
        type_ = type(style)
        if type_ not in cls._registry:
            raise ValueError(f'No builder registered for style: {type_}')
        return cls._registry[type_]


class Director:
    @staticmethod
    def render(register: Type[Register], style: WidgetStyle):
        builder = register.get_builder(style)(style)
        for child in getattr(style, 'children', []):
            Director.render(register, child)
        builder.run()
