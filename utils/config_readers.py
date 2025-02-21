import yaml
import logging

from .loaders import IncludeLoader

logger = logging.getLogger(__name__)


class ConfigReader:
    @staticmethod
    def read(filepath):
        with open(filepath, 'r') as f:
            data = yaml.load(f, IncludeLoader)
            logger.debug(f'ConfigReader read {filepath}: {data}')
        return data
