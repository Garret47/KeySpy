import logging
from settings import app_config
from utils import SchemaBuilderRegister, ConfigReader, TreeUi, MetaSingleton
from .schemas import Model, WidgetSchema

logger = logging.getLogger(__name__)


class UIManager:
    WINDOW: TreeUi | None = None

    @classmethod
    def render_main_window(cls, config: str = app_config.gui.FILENAME_MAIN_CONFIG):
        logger.info('Render main window')
        interface_main = ConfigReader.read(config, processor=Model)
        cls._render(interface_main, cls.WINDOW)

    @classmethod
    def render_compile_top_level(cls, config: str = app_config.gui.FILENAME_COMPILE_CONFIG):
        logger.info('Render Compile Toplevel')
        interface_compile = ConfigReader.read(config, processor=Model)
        cls._render(interface_compile, cls.WINDOW)

    @classmethod
    def _render(cls, interface: WidgetSchema, master: TreeUi | None = None):
        logger.debug(f'Render schema: {interface} - {interface.__class__.__name__}')
        widget = master.builder.widget if master else None
        current_elem = master.find(interface.name) if master else None
        if not current_elem:
            builder = SchemaBuilderRegister.get(interface)(interface, widget)
            master = TreeUi(interface.name, builder, parent=master)
        else:
            builder = None
            master = current_elem
        for child in getattr(interface, 'children', []):
            cls._render(child, master)
        cls.WINDOW = master.root
        if builder:
            builder.run()
