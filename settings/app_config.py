from dataclasses import dataclass, field
from pathlib import Path
import logging.config
import json


class AppConfigError(Exception):
    pass


@dataclass
class GUIConfig:
    FILENAME_MAIN_CONFIG = 'data/gui/main_window.yaml'


@dataclass
class AppConfig:
    FILE_LOGGING_CONFIG: str = 'data/logging.json'
    LOGGER_NAME: str = 'console'
    gui: GUIConfig = field(default_factory=GUIConfig)

    def configure_logging(self):
        logging_file = Path(self.FILE_LOGGING_CONFIG)
        if logging_file.exists():
            with open(logging_file, 'r') as f:
                LOGGING_CONFIG = json.load(f)
                logging.config.dictConfig(LOGGING_CONFIG)
        else:
            raise AppConfigError(f'file {self.FILE_LOGGING_CONFIG} not exists')


app_config = AppConfig()
