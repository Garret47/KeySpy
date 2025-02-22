import logging

from settings import env_config, app_config
from server import Server
from gui import UIManager
from utils import AsyncTkinter

app_config.configure_logging()
logger = logging.getLogger(__name__)

### TODO Изменить Director, убрать TkinterGUI, реализовать чтение через отдельный класс, убрать жесткую зависимость
### TODO между TkinterGUI и Register, перенести отдельные классы, убрать logging.json и заменить на yaml, добавить логгирование!!!


def main():
    server = Server(env_config.HOST, env_config.PORT)
    AsyncTkinter.get_event_loop().create_task(server.start())
    UIManager().render_main_window()


if __name__ == '__main__':
    main()
