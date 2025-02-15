from dataclasses import dataclass
from pathlib import Path
import logging.config
import json


class AppConfigError(Exception):
    pass


@dataclass
class AppConfig:
    FILE_LOGGING_CONFIG: str = 'data/logging.json'
    LOGGER_NAME: str = 'console'

    def configure_logging(self):
        logging_file = Path(self.FILE_LOGGING_CONFIG)
        if logging_file.exists():
            with open(logging_file, 'r') as f:
                LOGGING_CONFIG = json.load(f)
                logging.config.dictConfig(LOGGING_CONFIG)
        else:
            raise AppConfigError(f'file {self.FILE_LOGGING_CONFIG} not exists')


app_config = AppConfig()
