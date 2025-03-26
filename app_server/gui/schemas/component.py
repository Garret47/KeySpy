from pydantic import Field
from typing import Optional, Union, List, Callable, Literal

from .base import WidgetSchema, GridSchema


class ComponentSchema(WidgetSchema):
    type: Literal["Label", "Button"]
    grid: Optional[GridSchema] = Field(default_factory=GridSchema)


class TableviewSchema(ComponentSchema):
    type: Literal["Tableview"]
    bind: Optional[List[Union[str, Callable]]] = None
    selectmode: str = 'browse'


class InputSchema(ComponentSchema):
    type: Literal["Entry", "Spinbox"]
    insert: Optional[List[Union[int, str]]] = None
