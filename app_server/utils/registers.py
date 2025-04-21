import logging
import weakref
import tkinter as tk
from typing import Type, Callable

logger = logging.getLogger(__name__)


class SchemaBuilderRegister:
    _registry = {}

    @classmethod
    def registry(cls, schema_cls: Type):
        def wrapper(builder_cls: Type):
            logger.debug(f'Registry cls {schema_cls.__name__} - {builder_cls.__name__}')
            cls._registry[schema_cls] = builder_cls
            return builder_cls

        return wrapper

    @classmethod
    def get(cls, schema: object):
        type_ = type(schema)
        if type_ not in cls._registry:
            logger.exception(f'No registered for schema: {type_}')
            raise ValueError(f'No registered for schema: {type_}')
        return cls._registry[type_]


class EventHandlerRegister:
    _registry = {}

    @classmethod
    def registry(cls, method_name: str):
        def wrapper(method: Callable):
            cls._registry[method_name] = method
            return method
        return wrapper

    @classmethod
    def get(cls, method_name: str):
        if method_name not in cls._registry:
            logger.exception(f'No registered for method {method_name}')
            raise ValueError(f"No registered for method {method_name}")
        return cls._registry[method_name]


class WidgetRegistry:
    def __init__(self):
        self._registry = weakref.WeakValueDictionary()
        self._root_name = None
        self._widget_id_to_name = {}

    @property
    def root(self):
        return self._registry.get(self._root_name)

    def _destroy_widget(self, id_widget: int):
        if id_widget not in self._widget_id_to_name:
            return
        name = self._widget_id_to_name.pop(id_widget, None)
        self._registry.pop(name, None)
        if name == self._root_name:
            self._root_name = None
            logger.debug(f"Root window has been destroyed, {name}")
        else:
            logger.debug(f"Event destroy: widget '{name}'")
        logger.debug(f"Current registry: (size: {len(self._registry)}, names: {set(self._registry.keys())}")

    def _event_destroy_widget(self, event: tk.Event):
        self._destroy_widget(id(event.widget))

    @staticmethod
    def check_error(func):
        def wrapper(cls, *args, **kwargs):
            try:
                return func(cls, *args, **kwargs)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Error in {func.__name__}: {str(e)}")
        return wrapper

    @check_error
    def registry(self, name, widget):
        if isinstance(widget, tk.Tk) and self._root_name is None:
            self._root_name = name
        self._registry[name] = widget
        self._widget_id_to_name[id(widget)] = name
        widget.bind("<Destroy>", self._event_destroy_widget, add="+")
        weakref.finalize(widget, self._destroy_widget, id(widget))

    @check_error
    def get(self, name):
        widget = self._registry.get(name)
        if widget:
            if not widget.winfo_exists():
                logger.warning(f"Widget '{name}' (id={id(widget)}) does not exist. Cleaning up")
                self._destroy_widget(id(widget))
                return None
            return widget

    @check_error
    def all(self, exclude_hide=False):
        if exclude_hide:
            res = {name: widget for name, widget in self._registry.items() if widget.winfo_ismapped()}
        else:
            res = {name: widget for name, widget in self._registry.items()}
        logger.debug(f"Fetching all widgets. Current registry size: {len(self._registry)} "
                     f"Returning {len(res)} widgets, {res.keys()}")
        return res
