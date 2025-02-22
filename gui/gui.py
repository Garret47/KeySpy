import logging

from settings import app_config
from utils import ConfigReader
from .styles import ComponentStyle, ContainerStyle, ContainerComponentStyle, Model, WidgetStyle
from .builders import BuilderComponent, BuilderContainer, BuilderContainerComponent
from .registers import Register

logger = logging.getLogger(__name__)


class UIManager:
    Register.registry(ComponentStyle, BuilderComponent)
    Register.registry(ContainerStyle, BuilderContainer)
    Register.registry(ContainerComponentStyle, BuilderContainerComponent)

    def __init__(self):
        self.register = Register
        self._ui_interface = {}

    def render_main_window(self):
        logger.info('Render main window')
        style_main = ConfigReader.read(app_config.gui.FILENAME_MAIN_CONFIG)
        style_main = Model(model=style_main)
        self._render(style_main)

    def _render(self, style: WidgetStyle):
        logger.debug(f'Render: Style: {style} - {style.__class__.__name__}')
        builder = self.register.get_builder(style)(style)
        self._ui_interface[builder.widget] = style.model_dump(exclude={'children'})
        for child in getattr(style, 'children', []):
            self._render(child)
        builder.run()

    @property
    def interface(self):
        return self._ui_interface
