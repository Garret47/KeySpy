import logging

from utils import SchemaBuilderRegister
from .base import Builder
from gui.schemas import StyleSchema


logger = logging.getLogger(__name__)


@SchemaBuilderRegister.registry(StyleSchema)
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
