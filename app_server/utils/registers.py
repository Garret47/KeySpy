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
    _registry = {}
    _widget_id_to_name = {}
    _root = None

    @classmethod
    def __on_root_destroyed(cls, ref: weakref.ref):
        logger.debug("Root window has been destroyed.")
        cls._root = None

    @classmethod
    def _on_widget_destroy(cls, ref: weakref.ref, widget_id):
        name = cls._widget_id_to_name.pop(widget_id, None)
        cls._registry.pop(name, None)
        logger.info(f"GC clean, destroy triggered: strong references ended for '{name}' (id={widget_id})")

    @classmethod
    def _event_destroy_widget(cls, event: tk.Event):
        name = cls._widget_id_to_name.pop(id(event.widget), None)
        ref = cls._registry.pop(name, None)
        logger.debug(f"Event destroy: widget '{name}'")
        if isinstance(event.widget, tk.Tk):
            cls.__on_root_destroyed(ref)
        logger.debug(f"Current registry: (size: {len(cls._registry)}, names: {cls._registry.keys()})")

    @staticmethod
    def check_error(func):
        def wrapper(cls, *args, **kwargs):
            try:
                return func(cls, *args, **kwargs)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Error in {func.__name__}: {str(e)}")
        return wrapper

    @classmethod
    @check_error
    def registry(cls, name, widget):
        if isinstance(widget, tk.Tk):
            cls._root = weakref.ref(widget, cls.__on_root_destroyed)
        cls._registry[name] = weakref.ref(widget, lambda ref, n=name: cls._on_widget_destroy(ref, n))
        cls._widget_id_to_name[id(widget)] = name
        widget.bind("<Destroy>", cls._event_destroy_widget, add="+")

    @classmethod
    @check_error
    def get(cls, name):
        ref = cls._registry.get(name)
        if ref:
            widget = ref()
            if not widget.winfo_exists():
                logger.warning(f"Widget '{name}' (id={id(widget)}) does not exist. Cleaning up")
                cls._on_widget_destroy(ref, id(widget))
                return None
            return widget

    @classmethod
    @check_error
    def all(cls):
        logger.debug(f"Fetching all widgets. Current registry size: {len(cls._registry)}")
        res = {name: ref() for name, ref in cls._registry.items()}
        return res

    @classmethod
    @check_error
    def root(cls):
        root = cls._root() if cls._root else None
        logger.debug(f"Root widget: {root}")
        return root
