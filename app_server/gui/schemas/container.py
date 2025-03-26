from pydantic import field_validator, Field, BaseModel
from typing import Optional, Annotated, Union, Literal, List, Tuple, Callable, TypeAlias
from .base import WidgetSchema, GridConfigSchema, StyleSchema, ThemeSchema
from .component import ComponentSchema, TableviewSchema, InputSchema
from utils import Validator


base_children: TypeAlias = Union["ContainerComponentSchema", ComponentSchema, TableviewSchema, InputSchema]
window_children: TypeAlias = Union[base_children, "ToplevelSchema"]
schemas: TypeAlias = Union[window_children, "WindowSchema"]


class BaseContainerSchema(WidgetSchema):
    type: str
    grid_config: Optional[GridConfigSchema] = None
    children: Optional[List[Annotated[base_children, Field(discriminator='type')]]] = Field(default_factory=list)


class ToplevelSchema(BaseContainerSchema):
    type: Literal["Toplevel"]
    protocol: Optional[Tuple[str, Callable]] = None


class WindowSchema(BaseContainerSchema):
    type: Literal["Window"]
    themes: Optional[List[ThemeSchema]] = Field(exclude=True, default_factory=list)
    styles: Optional[List[StyleSchema]] = Field(exclude=True, default_factory=list)
    func: Optional[Tuple[int, Callable]] = Field(default_factory=list)
    children: Optional[List[Annotated[window_children, Field(discriminator='type')]]] = Field(default_factory=list)

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        Validator.validate_size(extra.get('size'), 'size')
        Validator.validate_size(extra.get('minsize'), 'minsize')
        return extra


class ContainerComponentSchema(BaseContainerSchema, ComponentSchema):
    type: Literal["Frame", "LabelFrame"]

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        return extra


class Model(BaseModel):
    model: schemas = Field(discriminator='type')

    def __new__(cls, interface):
        self = super().__new__(cls)
        super(Model, self).__init__(model=interface)
        return self.model
