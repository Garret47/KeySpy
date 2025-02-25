import ttkbootstrap as ttk
from pydantic import Field, BaseModel, model_validator, field_validator
from typing import Optional, Dict, Any, List, Type


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
