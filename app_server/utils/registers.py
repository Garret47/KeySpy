import logging
from typing import Type, Callable


logger = logging.getLogger(__name__)


class SchemaBuilderRegister:
    _registry = {}

    @classmethod
    def registry(cls, schema_cls: Type):
        def wrapper(builder_cls: Type):
            logger.debug(f'Registry cls {schema_cls.__name__} - {builder_cls.__name__}')
            cls._registry[schema_cls] = builder_cls
            return builder_cls
        return wrapper

    @classmethod
    def get(cls, schema: object):
        type_ = type(schema)
        if type_ not in cls._registry:
            logger.exception(f'No registered for schema: {type_}')
            raise ValueError(f'No registered for schema: {type_}')
        return cls._registry[type_]


class EventHandlerRegister:
    _registry = {}

    @classmethod
    def registry(cls, method_name: str):
        def wrapper(method: Callable):
            cls._registry[method_name] = method
            return method
        return wrapper

    @classmethod
    def get(cls, method_name: str):
        if method_name not in cls._registry:
            logger.exception(f'No registered for method {method_name}')
            raise ValueError(f"No registered for method {method_name}")
        return cls._registry[method_name]
