import yaml
import logging

from .loaders import Loader
from .cache import cache

logger = logging.getLogger(__name__)


class ConfigReader:
    @staticmethod
    @cache
    def read(filepath):
        with open(filepath, 'r') as f:
            data = yaml.load(f, Loader)
            logger.debug(f'ConfigReader read {filepath}: {data}')
        return data
