import logging
from typing import Union
from settings import app_config
from utils import SchemaBuilderRegister, ConfigReader, TreeUi, MetaSingleton
from gui.schemas import Model, WidgetSchema

logger = logging.getLogger(__name__)


class UIManager(metaclass=MetaSingleton):
    def __init__(self):
        self.window = None

    def render_main_window(self):
        logger.info('Render main window')
        interface_main = ConfigReader.read(app_config.gui.FILENAME_MAIN_CONFIG, processor=Model)
        self._render(interface_main)

    def _render(self, interface: WidgetSchema, master: Union[None, TreeUi] = None):
        logger.debug(f'Render schema: {interface} - {interface.__class__.__name__}')
        widget = master.builder.widget if master else None
        builder = SchemaBuilderRegister.get(interface)(interface, widget)
        master = TreeUi(interface.name, builder, parent=master)
        for child in getattr(interface, 'children', []):
            self._render(child, master)
        self.window = master
        builder.run()
