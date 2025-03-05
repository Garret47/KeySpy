import logging
from utils import EventHandlerRegister, AsyncTkinter
from .base import BaseEventHandler
from server import Server


logger = logging.getLogger(__name__)


class ViewMainBind:
    @staticmethod
    @EventHandlerRegister.registry('click_table')
    def click_tableview_element(event):
        logger.info('Click Table')
        server = Server()
        if event.widget.selection():
            logger.debug(f'Old selected keylogger - {server.selected_keylogger}')
            server.selected_keylogger = tuple(event.widget.master.get_row(iid=event.widget.selection()[0]).values)
            logger.debug(f'New selected keylogger - {server.selected_keylogger}')
        if server.selected_keylogger:
            BaseEventHandler.change_state_header_buttons('active')
