import logging
import tkinter as ttk

from settings import app_config
from utils import SchemaBuilderRegister, ConfigReader, MetaSingleton, WidgetRegistry
from .schemas import Model, WidgetSchema

logger = logging.getLogger(__name__)


class UIManager:

    @classmethod
    def render_main_window(cls, config: str = app_config.gui.FILENAME_MAIN_CONFIG):
        logger.info('Render main window')
        logger.debug(f"Widget Registry before creation: {WidgetRegistry.all().keys()}")
        interface_main = ConfigReader.read(config, processor=Model)
        root = WidgetRegistry.root()
        logger.info(f"Rendering schema with root: {root}, schema: {interface_main}")
        cls._render(interface_main, root)

    @classmethod
    def render_compile_top_level(cls, config: str = app_config.gui.FILENAME_COMPILE_CONFIG):
        logger.info('Render Compile Toplevel')
        logger.debug(f"Widget Registry before creation: {WidgetRegistry.all().keys()}")
        interface_compile = ConfigReader.read(config, processor=Model)
        root = WidgetRegistry.root()
        logger.info(f"Rendering schema with root: {root}, schema: {interface_compile}")
        cls._render(interface_compile, root)

    @classmethod
    def _render(cls, interface: WidgetSchema, master: ttk.Widget | None = None):
        current_elem = WidgetRegistry.get(interface.name)
        builder = None
        if not current_elem:
            builder = SchemaBuilderRegister.get(interface)(interface, master)
            current_elem = builder.widget
            WidgetRegistry.registry(interface.name, builder.widget)
        master = current_elem
        for child in getattr(interface, 'children', []):
            cls._render(child, master)
        if builder:
            builder.run()
