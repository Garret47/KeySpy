import tkinter as tk
import ttkbootstrap as ttk
import ttkbootstrap.tableview

from pydantic import BaseModel, model_validator, Field
from typing import Dict, Any, Type, List, Optional


SUPPORTED_CLASSES = {
    "Button": ttk.Button,
    "Frame": ttk.Frame,
    "Tableview": ttk.tableview.Tableview,
    "Label": ttk.Label,
    "Window": ttk.Window
}


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
        if self.type in SUPPORTED_CLASSES:
            self.tk_class = SUPPORTED_CLASSES[self.type]
            return self
        raise ValueError(f'Type {self.type} is not supported')
