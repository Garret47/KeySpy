import logging
import tkinter as ttk

from settings import app_config
from utils import SchemaBuilderRegister, ConfigReader, MetaSingleton, WidgetRegistry
from .schemas import Model, WidgetSchema

logger = logging.getLogger(__name__)


class UIManager:
    REGISTER = WidgetRegistry()

    @classmethod
    def render_window(cls, config):
        logger.info(f'Render window: {config}')
        logger.debug(f"Widget Registry before creation: {cls.REGISTER.all(exclude_hide=True).keys()}")
        interface_window = ConfigReader.read(config, processor=Model)
        logger.info(f"Rendering schema with root: {cls.REGISTER.root}, schema: {interface_window.interface}")
        cls._hide_interface_diff(interface_window.names)
        cls._render(interface_window.interface, cls.REGISTER.root)

    @classmethod
    def render_top_level(cls, config):
        logger.info(f'Render Toplevel: {config}')
        logger.debug(f"Widget Registry before creation: {cls.REGISTER.all(exclude_hide=True).keys()}")
        interface_toplevel = ConfigReader.read(config, processor=Model)
        logger.info(f"Rendering schema with root: {cls.REGISTER.root}, schema: {interface_toplevel.interface}")
        cls._render(interface_toplevel.interface, cls.REGISTER.root)

    @classmethod
    def _render(cls, interface: WidgetSchema, master: ttk.Widget | None = None):
        current_elem = cls.REGISTER.get(interface.name)
        builder = None
        if current_elem:
            if not current_elem.winfo_ismapped():
                current_elem.grid()
        else:
            builder = SchemaBuilderRegister.get(interface)(interface, master)
            current_elem = builder.widget
            cls.REGISTER.registry(interface.name, builder.widget)
        master = current_elem
        for child in getattr(interface, 'children', []):
            cls._render(child, master)
        if builder:
            builder.run()

    @classmethod
    def _hide_interface_diff(cls, new_interface_names: set[str]):
        current_interface_names = set(cls.REGISTER.all(exclude_hide=True).keys())
        hidden_widget_names = current_interface_names - new_interface_names
        logger.debug(f'Hide widgets: {hidden_widget_names}')
        for name in hidden_widget_names:
            widget = cls.REGISTER.get(name)
            widget.grid_remove()
