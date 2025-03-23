from typing import Optional, Callable


def cache(function_read: Callable):
    _cache = {}

    def wrapper(filepath: str, processor: Optional[Callable] = None, force_reload: bool = False):
        if filepath in _cache and not force_reload:
            return _cache[filepath]
        result = function_read(filepath)
        if processor is not None:
            result = processor(result)
        _cache[filepath] = result
        return result

    return wrapper
