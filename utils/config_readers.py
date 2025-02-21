import yaml

from .loaders import IncludeLoader


class ConfigReader:
    @staticmethod
    def read(filepath):
        with open(filepath, 'r') as f:
            data = yaml.load(f, IncludeLoader)
        return data
