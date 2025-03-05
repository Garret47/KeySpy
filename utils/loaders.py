import yaml
import os.path

from .registers import EventHandlerRegister


class LoaderMeta(type):
    def __new__(metacls, __name__, __bases__, __dict__):
        cls = super().__new__(metacls, __name__, __bases__, __dict__)
        if hasattr(cls, 'add_constructor') and hasattr(cls, 'include') and hasattr(cls, 'method'):
            cls.add_constructor('!include', cls.include)
            cls.add_constructor('!method', cls.method)
        else:
            raise yaml.YAMLError(f'Class {cls.__name__} is missing the required method for YAML processing')
        return cls


class Loader(yaml.Loader, metaclass=LoaderMeta):
    def __init__(self, stream):
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)

    def include(self, node):
        filename = os.path.abspath(os.path.join(self._root, self.construct_scalar(node)))
        extension = os.path.splitext(filename)[1].lstrip('.')

        with open(filename, 'r') as f:
            if extension in ('yaml', 'yml'):
                return yaml.load(f, Loader)
            else:
                return ''.join(f.readlines())

    def method(self, node):
        function_name = self.construct_scalar(node)
        function = EventHandlerRegister.get(function_name)
        return function
