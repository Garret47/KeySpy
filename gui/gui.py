import logging

from settings import app_config
from utils import ConfigReader
from .styles import ComponentStyle, ContainerStyle, ContainerComponentStyle, Model
from .builders import BuilderComponent, BuilderContainer, BuilderContainerComponent
from .registers import Register
from .directors import Director

logger = logging.getLogger(__name__)


class UIManager:
    Register.registry(ComponentStyle, BuilderComponent)
    Register.registry(ContainerStyle, BuilderContainer)
    Register.registry(ContainerComponentStyle, BuilderContainerComponent)

    @staticmethod
    def render_main_window():
        logger.info('Render main window')
        style_main = ConfigReader.read(app_config.gui.FILENAME_MAIN_CONFIG)
        style_main = Model(model=style_main)
        Director.render(Register, style_main)
