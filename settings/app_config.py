from dataclasses import dataclass, field
import logging.config

from utils import ConfigReader


class AppConfigError(Exception):
    pass


@dataclass
class GUIConfig:
    FILENAME_MAIN_CONFIG = 'data/gui/main_window.yaml'
    FILENAME_STYLES_CONFIG = 'data/gui/styles.yaml'


@dataclass
class AppConfig:
    FILE_LOGGING_CONFIG: str = 'data/logging.yaml'
    LOGGER_NAME: str = 'console'
    gui: GUIConfig = field(default_factory=GUIConfig)

    def configure_logging(self):
        LOGGING_CONFIG = ConfigReader.read(self.FILE_LOGGING_CONFIG)
        logging.config.dictConfig(LOGGING_CONFIG)


app_config = AppConfig()
