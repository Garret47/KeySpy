import tkinter as tk
import ttkbootstrap as ttk
import ttkbootstrap.tableview

from pydantic import BaseModel, model_validator, Field
from typing import Dict, Any, Type, List, Optional, Union

SUPPORTED_CLASSES = {
    "Button": ttk.Button,
    "Frame": ttk.Frame,
    "Tableview": ttk.tableview.Tableview,
    "Label": ttk.Label,
    "Window": ttk.Window,
    "Toplevel": ttk.Toplevel,
    "LabelFrame": ttk.LabelFrame,
    "Entry": ttk.Entry,
    "Spinbox": ttk.Spinbox
}


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


class GridSchema(BaseModel):
    row: Optional[int] = Field(ge=0, default=None)
    column: Optional[int] = Field(ge=0, default=None)
    rowspan: Optional[int] = Field(ge=0, default=None)
    columnspan: Optional[int] = Field(ge=0, default=None)
    sticky: Optional[str] = Field(min_length=1, max_length=4, default=None)
    padx: Optional[Union[int | list]] = Field(default=None)
    pady: Optional[Union[int | list]] = Field(default=None)
    ipadx: Optional[Union[int | list]] = Field(default=None)
    ipady: Optional[Union[int | list]] = Field(default=None)


class StyleSchema(BaseModel):
    name: str
    master: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    map: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @model_validator(mode='after')
    @classmethod
    def validate_config_map(cls, values):
        values.config['style'] = values.name
        values.map['style'] = values.name

        return values


class WidgetSchema(BaseModel):
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)
    type: str
    name: str = Field(min_length=1, description='Unique names')
    tk_class: Type[tk.Widget] = Field(exclude=True, default=None)

    @model_validator(mode='after')
    def set_tk_class(self):
        if self.type in SUPPORTED_CLASSES:
            self.tk_class = SUPPORTED_CLASSES[self.type]
            return self
        raise ValueError(f'Type {self.type} is not supported')
