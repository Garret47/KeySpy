import logging
from abc import ABC, abstractmethod
from typing import Union

from .ui_config import WidgetSchema, StyleSchema
from utils import AsyncTkinter


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


class BuilderContainer(Builder):
    def place_window_center(self):
        self.widget.place_window_center()
        return self

    def configure_grid(self):
        if self.schema.grid_config is None:
            return

        for i in range(self.schema.grid_config.rows):
            self.widget.rowconfigure(i, weight=self.schema.grid_config.r_weights[i])

        for i in range(self.schema.grid_config.columns):
            self.widget.columnconfigure(i, weight=self.schema.grid_config.c_weights[i])

    def configure(self):
        self.place_window_center()
        self.configure_grid()
        for child in self.schema.children:
            if hasattr(child, 'extra'):
                child.extra.update(master=self.widget)

    def run(self):
        AsyncTkinter.async_mainloop(self.widget)


class BuilderComponent(Builder):
    def run(self):
        if self.schema.grid is not None:
            self.widget.grid(**self.schema.grid.extra)
        else:
            self.widget.grid()


class BuilderContainerComponent(BuilderContainer, BuilderComponent):
    def place_window_center(self):
        pass

    def run(self):
        super(BuilderContainer, self).run()


class BuilderStyle(Builder):
    def reset(self, schema: StyleSchema):
        logger.info(f'{self.__class__.__name__} reset {schema}')
        self.schema = schema
        self._root = self.schema.tk_class(self.schema.master)
        self.configure()

    def configure(self):
        if self.schema.config is not None:
            self.widget.configure(**self.schema.config)
        if self.schema.map is not None:
            self.widget.map(**self.schema.map)
