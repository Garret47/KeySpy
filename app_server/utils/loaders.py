import yaml
import logging
import os.path

from pydantic import SecretStr
from operator import attrgetter
from settings import app_config, user_config
from .registers import EventHandlerRegister

logger = logging.getLogger(__name__)


class LoaderMeta(type):
    def __new__(metacls, __name__, __bases__, __dict__):
        cls = super().__new__(metacls, __name__, __bases__, __dict__)
        all_methods = ['add_constructor', 'include', 'method', 'var', 'user_var']
        if all(hasattr(cls, method_name) for method_name in all_methods):
            all_tags = {'!include': cls.include, '!method': cls.method, '!var': cls.var, '!user_var': cls.user_var}
        else:
            raise yaml.YAMLError(f'Class {cls.__name__} is missing the required method for YAML processing')
        for tag, method in all_tags.items():
            cls.add_constructor(tag, method)
        cls.ALLOWED_TAGS = list(all_tags.keys())
        return cls


class Loader(yaml.Loader, metaclass=LoaderMeta):
    DEFAULT_RETURN_VAR: str = ''

    def __init__(self, stream):
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)

    @staticmethod
    def inner_tag_resolver(func):
        def wrapper(self, node, *args, **kwargs):
            for tag in self.ALLOWED_TAGS:
                if node.value.strip().startswith(tag):
                    constructor = self.yaml_constructors.get(tag)
                    node.value = constructor(self, yaml.compose(node.value))
                    break
            return func(self, node, *args, **kwargs)
        return wrapper

    def include(self, node):
        filename = os.path.abspath(os.path.join(self._root, self.construct_scalar(node)))
        extension = os.path.splitext(filename)[1].lstrip('.')

        with open(filename, 'r') as f:
            if extension in ('yaml', 'yml'):
                return yaml.load(f, Loader)
            else:
                return ''.join(f.readlines())

    @inner_tag_resolver
    def method(self, node):
        function_name = self.construct_scalar(node)
        function = EventHandlerRegister.get(function_name)
        return function

    def _resolve_variable_path(self, path: str, source: object):
        try:
            resolved_value = attrgetter(path)(source)
            logger.debug(f'Resolved variable path "{path}" to value: {resolved_value!r}')
            return resolved_value
        except AttributeError as e:
            logger.warning(
                f'Unable to resolve path "{path}" in source {getattr(source, "__name__", repr(source))}: {e}'
                f'Falling back to default: {self.DEFAULT_RETURN_VAR!r}'
            )
            return self.DEFAULT_RETURN_VAR

    def var(self, node):
        path = self.construct_scalar(node)
        return self._resolve_variable_path(path, app_config.gui.keys)

    def user_var(self, node):
        path = self.construct_scalar(node)
        path_resolve = self._resolve_variable_path(path, user_config.credentials)
        if isinstance(path_resolve, SecretStr):
            return path_resolve.get_secret_value()
        return path_resolve
