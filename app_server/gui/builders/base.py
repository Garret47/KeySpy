import logging
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Union

from gui.schemas import WidgetSchema


logger = logging.getLogger(__name__)


class InterfaceBuilder(ABC):
    @abstractmethod
    def __init__(self, style: WidgetSchema, master: Union[None, tk.Widget] = None):
        pass

    @abstractmethod
    def reset(self, style: WidgetSchema, master: Union[None, tk.Widget] = None):
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
    def __init__(self, schema: WidgetSchema, master: Union[None, tk.Widget] = None):
        self.schema = None
        self._root = None
        self.reset(schema, master)

    def reset(self, schema: WidgetSchema, master: Union[None, tk.Widget] = None):
        logger.info(f'{self.__class__.__name__} reset {schema}')
        self.schema = schema
        if master:
            self._root = self.schema.tk_class(master=master, **self.schema.extra)
        else:
            self._root = self.schema.tk_class(**self.schema.extra)
        self.configure()

    def configure(self):
        pass

    def run(self):
        pass

    @property
    def widget(self):
        return self._root
