import tkinter as tk
import ttkbootstrap as ttk
from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Dict, Any, Type, List, Optional, Union, Literal, Annotated

from utils import Validator


class Extra(BaseModel):
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class GridConfigSchema(BaseModel):
    rows: int
    columns: int
    r_weights: List[int]
    c_weights: List[int]

    @model_validator(mode='after')
    def validate_model(self):
        if self.rows != len(self.r_weights):
            raise ValueError(f'Rows ({self.rows}) must match the length of weights {len(self.r_weights)}')
        if self.columns != len(self.c_weights):
            raise ValueError(f'Columns ({self.columns}) must match the length of weights {len(self.c_weights)}')
        return self


class WidgetSchema(Extra):
    type: str

    tk_class: Type[tk.Widget] = Field(exclude=True, default=None)

    @model_validator(mode='after')
    def set_tk_class(self):
        self.tk_class = getattr(ttk, self.type, None)
        if self.tk_class is None:
            raise ValueError(f'Type {self.type} is not supported')
        return self


class ComponentSchema(WidgetSchema):
    type: Literal['Button']
    grid: Optional[Extra] = None


class ContainerSchema(WidgetSchema):
    type: Literal['Window']
    grid_config: Optional[GridConfigSchema] = None
    children: Optional[List[
        Annotated[
            Union["ContainerComponentSchema", "ComponentSchema"], Field(discriminator='type')
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
    type: Literal['Frame']
    children: Optional[List[ComponentSchema]] = Field(default_factory=list)

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        return extra


class StyleSchema(BaseModel):
    name: str
    master: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    map: Optional[Dict[str, Any]] = None

    tk_class: Type[ttk.Style] = Field(exclude=True, default=None)

    @model_validator(mode='after')
    @classmethod
    def validate_config_map(cls, values):
        if getattr(values, 'config'):
            values.config['style'] = values.name
        if getattr(values, 'map'):
            values.map['style'] = values.name

        return values

    @model_validator(mode='after')
    def set_tk_class(self):
        self.tk_class = ttk.Style
        return self


class Model(BaseModel):
    model: Union[ContainerSchema, ContainerComponentSchema, ComponentSchema] = Field(discriminator='type')

    def __new__(cls, **kwargs):
        self = super().__new__(cls)
        super(Model, self).__init__(**kwargs)
        return self.model


class ModelStyle(BaseModel):
    model: List[StyleSchema] = None

    @field_validator('model', mode='before')
    @classmethod
    def set_empty_list(cls, values):
        if values is None:
            values = []
        return values

    def __new__(cls, **kwargs):
        self = super().__new__(cls)
        super(ModelStyle, self).__init__(**kwargs)
        return self.model
