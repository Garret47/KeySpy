import logging
from typing import Type

from .registers import Register
from .styles import WidgetStyle


logger = logging.getLogger(__name__)


class Director:
    @staticmethod
    def render(register: Type[Register], style: WidgetStyle):
        logger.debug(f'Director render: Style: {style} - {style.__class__.__name__}')
        builder = register.get_builder(style)(style)
        for child in getattr(style, 'children', []):
            Director.render(register, child)
        builder.run()
