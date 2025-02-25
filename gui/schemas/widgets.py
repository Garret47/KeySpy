from pydantic import field_validator, Field, BaseModel
from typing import Optional, Annotated, Union, Literal, List

from .base import WidgetSchema, Extra, GridConfigSchema
from utils import Validator


class ComponentSchema(WidgetSchema):
    type: Literal['Button', 'Label']
    grid: Optional[Extra] = None


class ContainerSchema(WidgetSchema):
    type: Literal['Window']
    grid_config: Optional[GridConfigSchema] = None
    children: Optional[List[
        Annotated[
            Union["ContainerComponentSchema", "ComponentSchema", "TableviewSchema"], Field(discriminator='type')
        ]
    ]] = Field(default_factory=list)

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        Validator.validate_size(extra.get('size'), 'size')
        Validator.validate_size(extra.get('minsize'), 'minsize')
        return extra


class ContainerComponentSchema(ContainerSchema, ComponentSchema):
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
    bind: Optional[List[str]] = None


class Model(BaseModel):
    model: Union[
        ContainerSchema,
        ContainerComponentSchema,
        TableviewSchema,
        ComponentSchema] = Field(discriminator='type')

    def __new__(cls, **kwargs):
        self = super().__new__(cls)
        super(Model, self).__init__(**kwargs)
        return self.model
