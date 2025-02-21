import logging
from abc import ABC, abstractmethod

from .styles import WidgetStyle
from utils import AsyncTkinter


logger = logging.getLogger(__name__)


class InterfaceBuilder(ABC):
    @abstractmethod
    def __init__(self, style: WidgetStyle):
        pass

    @abstractmethod
    def reset(self, style: WidgetStyle):
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
    def __init__(self, style: WidgetStyle):
        self.style = None
        self._root = None
        self.reset(style)

    def reset(self, style: WidgetStyle):
        logger.info(f'{self.__class__.__name__} reset {style}')
        self.style = style
        self._root = self.style.tk_class(**self.style.extra)
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
        if self.style.grid_config is None:
            return

        for i in range(self.style.grid_config.rows):
            self.widget.rowconfigure(i, weight=self.style.grid_config.r_weights[i])

        for i in range(self.style.grid_config.columns):
            self.widget.columnconfigure(i, weight=self.style.grid_config.c_weights[i])

    def configure(self):
        self.place_window_center()
        self.configure_grid()
        for child in self.style.children:
            child.extra.update(master=self.widget)

    def run(self):
        AsyncTkinter.async_mainloop(self.widget)


class BuilderComponent(Builder):
    def run(self):
        if self.style.grid is not None:
            self.widget.grid(**self.style.grid.extra)
        else:
            self.widget.grid()


class BuilderContainerComponent(BuilderContainer, BuilderComponent):
    def place_window_center(self):
        pass

    def run(self):
        super(BuilderContainer, self).run()
