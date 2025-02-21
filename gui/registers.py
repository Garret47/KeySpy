import logging
from typing import Type

from .styles import WidgetStyle
from .builders import InterfaceBuilder


logger = logging.getLogger(__name__)


class Register:
    _registry: dict = {}

    @classmethod
    def registry(cls, style_cls: Type[WidgetStyle], builder_cls: Type[InterfaceBuilder]):
        logger.debug(f'Registry {style_cls.__name__} - {builder_cls.__name__}')
        cls._registry[style_cls] = builder_cls

    @classmethod
    def get_builder(cls, style: WidgetStyle):
        type_ = type(style)
        if type_ not in cls._registry:
            raise ValueError(f'No builder registered for style: {type_}')
        return cls._registry[type_]
