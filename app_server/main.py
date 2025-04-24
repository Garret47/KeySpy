import logging.config

from settings import app_config, user_config
from server import Server
from gui import UIManager
from utils import AsyncTkinter, ConfigReader
from handlers import *

LOGGING_CONFIG = ConfigReader.read(app_config.FILE_LOGGING_CONFIG)
logging.config.dictConfig(LOGGING_CONFIG)
if not user_config.DEBUG:
    logging.disable(logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    server = Server(user_config.server.LISTEN_HOST, user_config.server.LISTEN_PORT)
    AsyncTkinter.get_event_loop().create_task(server.start())
    UIManager.render_window(app_config.gui.config.FILENAME_MAIN_CONFIG)


if __name__ == '__main__':
    main()
