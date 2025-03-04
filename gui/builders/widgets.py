from ttkbootstrap import Style

from utils import AsyncTkinter, SchemaBuilderRegister
from .base import Builder
from gui.schemas import ComponentSchema, ContainerComponentSchema, WindowSchema, TableviewSchema


@SchemaBuilderRegister.registry(WindowSchema)
class BuilderWindow(Builder):
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

    def configure_styles(self):
        for style in self.schema.styles:
            style_cls = Style(style.master)
            style_cls.configure(**style.config)
            style_cls.map(**style.map)

    def configure(self):
        self.place_window_center()
        self.configure_grid()
        self.configure_styles()

    def run(self):
        AsyncTkinter.async_mainloop(self.widget)


@SchemaBuilderRegister.registry(ComponentSchema)
class BuilderComponent(Builder):
    def run(self):
        self.widget.grid(**self.schema.grid.model_dump(exclude_none=True))


@SchemaBuilderRegister.registry(ContainerComponentSchema)
class BuilderContainerComponent(BuilderWindow, BuilderComponent):
    def place_window_center(self):
        pass

    def configure_styles(self):
        pass

    def run(self):
        super(BuilderWindow, self).run()


@SchemaBuilderRegister.registry(TableviewSchema)
class BuilderTableview(BuilderComponent):
    def configure(self):
        if self.schema.bind is not None:
            self.widget.view.bind(*self.schema.bind)
