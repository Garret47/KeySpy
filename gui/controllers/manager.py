import logging
from settings import app_config
from utils import SchemaBuilderRegister, ConfigReader
from gui.schemas import Model, WidgetSchema

logger = logging.getLogger(__name__)


class UIManager:
    def __init__(self):
        self._ui_interface = {}

    def render_main_window(self):
        logger.info('Render main window')
        interface_main = ConfigReader.read(app_config.gui.FILENAME_MAIN_CONFIG, processor=Model)
        self._render(interface_main)

    def _render(self, interface: WidgetSchema):
        logger.debug(f'Render: Style: {interface} - {interface.__class__.__name__}')
        builder = SchemaBuilderRegister.get(interface)(interface)
        self._ui_interface[builder.widget] = interface.model_dump(exclude={'children'})
        for child in getattr(interface, 'children', []):
            self._render(child)
        builder.run()
