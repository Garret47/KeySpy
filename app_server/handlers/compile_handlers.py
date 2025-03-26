import logging
from gui import UIManager
from utils import EventHandlerRegister, AsyncTkinter


logger = logging.getLogger(__name__)

class CompileHandler:
    @staticmethod
    @EventHandlerRegister.registry("close_toplevel")
    @AsyncTkinter.async_handler
    async def close_toplevel():
        logger.info('Close Toplevel Compile')
        logger.debug(f'Window before close: {list(elem.name for elem in UIManager.WINDOW.children)}')
        toplevel = UIManager.WINDOW.find('compile_toplevel')
        toplevel.builder.widget.destroy()
        toplevel.clear()
        logger.debug(f'Window after close: {list(elem.name for elem in UIManager.WINDOW.children)}')
        btn = UIManager.WINDOW.find('btn_create')
        btn.builder.widget.config(state='normal')
