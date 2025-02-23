import logging

from settings import app_config
from utils import ConfigReader
from .ui_config import (ComponentSchema, ContainerSchema, ContainerComponentSchema,
                        Model, WidgetSchema, StyleSchema, ModelStyle)
from .builders import BuilderComponent, BuilderContainer, BuilderContainerComponent, BuilderStyle
from .registers import Register

logger = logging.getLogger(__name__)


class UIManager:
    Register.registry(ComponentSchema, BuilderComponent)
    Register.registry(ContainerSchema, BuilderContainer)
    Register.registry(ContainerComponentSchema, BuilderContainerComponent)
    Register.registry(StyleSchema, BuilderStyle)

    def __init__(self):
        self.register = Register
        self._ui_interface = {}

    def render_main_window(self):
        logger.info('Render main window')
        interface_main = ConfigReader.read(app_config.gui.FILENAME_MAIN_CONFIG)
        styles = ConfigReader.read(app_config.gui.FILENAME_STYLES_CONFIG)
        interface_main = Model(model=interface_main)
        styles = ModelStyle(model=styles)
        interface_main.children = styles + interface_main.children
        self._render(interface_main)

    def _render(self, style: WidgetSchema):
        logger.debug(f'Render: Style: {style} - {style.__class__.__name__}')
        builder = self.register.get_builder(style)(style)
        if isinstance(builder.widget, WidgetSchema):
            self._ui_interface[builder.widget] = style.model_dump(exclude={'children'})
        for child in getattr(style, 'children', []):
            self._render(child)
        builder.run()

    @property
    def interface(self):
        return self._ui_interface
