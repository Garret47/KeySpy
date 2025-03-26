from utils import SchemaBuilderRegister
from .base import Builder
from gui.schemas import ComponentSchema, TableviewSchema, InputSchema


@SchemaBuilderRegister.registry(ComponentSchema)
class BuilderComponent(Builder):
    def run(self):
        self.widget.grid(**self.schema.grid.model_dump(exclude_none=True))


@SchemaBuilderRegister.registry(TableviewSchema)
class BuilderTableview(BuilderComponent):
    def configure(self):
        if self.schema.bind is not None:
            self.widget.view.bind(*self.schema.bind)
        self.widget.configure(selectmode=self.schema.selectmode)


@SchemaBuilderRegister.registry(InputSchema)
class BuilderInput(BuilderComponent):
    def configure(self):
        if self.schema.insert is not None:
            self.widget.insert(*self.schema.insert)
