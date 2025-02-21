import tkinter as tk
import ttkbootstrap as ttk
from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Dict, Any, Type, List, Optional, Union, Literal, Annotated

from utils import Validator


class Extra(BaseModel):
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class GridConfig(BaseModel):
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


class GridStyle(Extra):
    pass


class WidgetStyle(Extra):
    type: str

    tk_class: Type[tk.Widget] = Field(exclude=True, default=None)

    @model_validator(mode='after')
    def set_tk_class(self):
        self.tk_class = getattr(ttk, self.type, None)
        if self.tk_class is None:
            raise ValueError(f'Type {self.type} is not supported')
        return self


class ComponentStyle(WidgetStyle):
    type: Literal['Button']
    grid: Optional[GridStyle] = None


class ContainerStyle(WidgetStyle):
    type: Literal['Window']
    grid_config: Optional[GridConfig] = None
    children: Optional[List[
        Annotated[
            Union["ContainerComponentStyle", "ComponentStyle"], Field(discriminator='type')
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


class ContainerComponentStyle(ContainerStyle, ComponentStyle):
    type: Literal['Frame']
    children: Optional[List[ComponentStyle]] = Field(default_factory=list)

    @field_validator('extra', mode='before')
    @classmethod
    def validate_extra(cls, extra: dict):
        Validator.validate_type_size(extra.get('size'), 'size')
        Validator.validate_type_size(extra.get('minsize'), 'minsize')
        return extra


class Model(BaseModel):
    model: Union[ContainerStyle, ContainerComponentStyle, ComponentStyle] = Field(discriminator='type')

    def __new__(cls, **kwargs):
        self = super().__new__(cls)
        super(Model, self).__init__(**kwargs)
        return self.model
