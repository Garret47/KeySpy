from ttkbootstrap import Style

from utils import AsyncTkinter, SchemaBuilderRegister
from .base import Builder
from .component import BuilderComponent
from gui.schemas import ContainerComponentSchema, WindowSchema, ToplevelSchema


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
        AsyncTkinter.async_mainloop(self.widget, *self.schema.func)


@SchemaBuilderRegister.registry(ToplevelSchema)
class BuilderToplevel(BuilderWindow):
    def place_window_center(self):
        width = self.widget.winfo_width()
        height = self.widget.winfo_height()
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.widget.geometry(f'+{x}+{y}')
        return self

    def configure_styles(self):
        pass

    def configure(self):
        self.widget.withdraw()
        self.place_window_center()
        self.configure_grid()
        if self.schema.protocol:
            self.widget.protocol(*self.schema.protocol)

    def run(self):
        self.widget.deiconify()


@SchemaBuilderRegister.registry(ContainerComponentSchema)
class BuilderContainerComponent(BuilderWindow, BuilderComponent):
    def place_window_center(self):
        pass

    def configure_styles(self):
        pass

    def run(self):
        super(BuilderWindow, self).run()