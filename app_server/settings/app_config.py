from dataclasses import dataclass, field
from pathlib import Path
import logging.config

from utils import ConfigReader


class AppConfigError(Exception):
    pass


@dataclass
class CompileConfig:
    ENV_EMAIL_USERNAME: str = "EMAIL_USERNAME"
    ENV_EMAIL_PASSWORD: str = "EMAIL_PASSWORD"
    ENV_EMAIL_PORT: str = "EMAIL_PORT"
    ENV_EMAIL_SERVER: str = "EMAIL_SERVER"
    ENV_EMAIL_DURATION: str = "DURATION"
    ENV_SERVER_IP: str = "SERVER_IP"
    ENV_SERVER_PORT: str = "SERVER_PORT_STR"


@dataclass
class GUIConfig:
    FILENAME_MAIN_CONFIG: Path = Path('data/gui/main_window.yaml')
    FILENAME_COMPILE_CONFIG: Path = Path('data/gui/widgets/compile_toplevel/toplevel.yaml')


@dataclass
class AppConfig:
    print('dawdwdwada')
    FILE_LOGGING_CONFIG: Path = Path('data/logging.yaml')
    LOGGER_NAME: str = 'console'
    CLIENT_DIR: Path = Path('../app_client/')
    gui: GUIConfig = field(default_factory=GUIConfig)
    compile: CompileConfig = field(default_factory=CompileConfig)

    def configure_logging(self):
        LOGGING_CONFIG = ConfigReader.read(self.FILE_LOGGING_CONFIG)
        logging.config.dictConfig(LOGGING_CONFIG)


app_config = AppConfig()
