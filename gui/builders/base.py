import logging
from abc import ABC, abstractmethod
from typing import Union

from gui.schemas import WidgetSchema, StyleSchema


logger = logging.getLogger(__name__)


class InterfaceBuilder(ABC):
    @abstractmethod
    def __init__(self, style: Union[WidgetSchema, StyleSchema]):
        pass

    @abstractmethod
    def reset(self, style: Union[WidgetSchema, StyleSchema]):
        pass

    @property
    @abstractmethod
    def widget(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def configure(self):
        pass


class Builder(InterfaceBuilder, ABC):
    def __init__(self, schema: Union[WidgetSchema, StyleSchema]):
        self.schema = None
        self._root = None
        self.reset(schema)

    def reset(self, schema: Union[WidgetSchema, StyleSchema]):
        logger.info(f'{self.__class__.__name__} reset {schema}')
        self.schema = schema
        self._root = self.schema.tk_class(**self.schema.extra)
        self.configure()

    def configure(self):
        pass

    def run(self):
        pass

    @property
    def widget(self):
        return self._root
