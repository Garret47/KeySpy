from utils import AsyncTkinter
from .base import Builder


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


class BuilderTableview(BuilderComponent):
    def configure(self):
        if self.schema.bind is not None:
            self.widget.bind(*self.schema.bind)
