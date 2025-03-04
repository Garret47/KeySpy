from pydantic import field_validator, Field, BaseModel
from typing import Optional, Annotated, Union, Literal, List, Callable

from .base import WidgetSchema, GridConfigSchema, GridSchema, StyleSchema
from utils import Validator


class ComponentSchema(WidgetSchema):
    type: Literal['Button', 'Label']
    grid: Optional[GridSchema] = Field(default_factory=GridSchema)


class BaseContainerSchema(WidgetSchema):
    type: str
    grid_config: Optional[GridConfigSchema] = None


class WindowSchema(BaseContainerSchema):
    type: Literal['Window']
    children: Optional[List[
        Annotated[
            Union["ContainerComponentSchema", "ComponentSchema", "TableviewSchema"], Field(discriminator='type')
        ]
    ]] = Field(default_factory=list)
    styles: Optional[List[StyleSchema]] = Field(exclude=True, default=None)

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        Validator.validate_size(extra.get('size'), 'size')
        Validator.validate_size(extra.get('minsize'), 'minsize')
        return extra


class ContainerComponentSchema(BaseContainerSchema, ComponentSchema):
    type: Literal["Frame"]
    children: Optional[List[
        Annotated[
            Union[ComponentSchema, "ContainerComponentSchema", "TableviewSchema"], Field(discriminator='type')
        ]
    ]] = Field(default_factory=list)

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        return extra


class TableviewSchema(ComponentSchema):
    type: Literal['Tableview']
    bind: Optional[List[Union[str, Callable]]] = None


class Model(BaseModel):
    model: Union[
        WindowSchema,
        ContainerComponentSchema,
        TableviewSchema,
        ComponentSchema] = Field(discriminator='type')

    def __new__(cls, interface):
        self = super().__new__(cls)
        super(Model, self).__init__(model=interface)
        return self.model
