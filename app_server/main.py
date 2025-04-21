import logging.config

from settings import env_config, app_config
from server import Server
from gui import UIManager
from utils import AsyncTkinter, ConfigReader
from handlers import *

LOGGING_CONFIG = ConfigReader.read(app_config.FILE_LOGGING_CONFIG)
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def main():
    server = Server(env_config.HOST, env_config.PORT)
    AsyncTkinter.get_event_loop().create_task(server.start())
    UIManager.render_window(app_config.gui.FILENAME_MAIN_CONFIG)


if __name__ == '__main__':
    main()
