import logging

from .base import BaseEventHandler
from settings import app_config
from server import Server
from utils import EventHandlerRegister, AsyncTkinter


logger = logging.getLogger(__name__)


class ViewMainBind:
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_TABLE)
    def click_tableview_element(event):
        logger.info('Click Table')
        server = Server()
        if event.widget.selection():
            logger.debug(f'Old selected keylogger - {server.selected_keylogger}')
            server.selected_keylogger = tuple(event.widget.master.get_row(iid=event.widget.selection()[0]).values)
            logger.debug(f'New selected keylogger - {server.selected_keylogger}')
        if server.selected_keylogger:
            BaseEventHandler.change_state_header_buttons('active')
