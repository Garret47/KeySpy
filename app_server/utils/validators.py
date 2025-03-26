from typing import Union


class Validator:
    @staticmethod
    def validate_type_size(size: Union[None, tuple, list], type_: str):
        if size is None:
            return
        if not isinstance(size, (tuple, list)) or len(size) != 2:
            raise TypeError(f'{type_} must be a list or tuple of length 2: {size}')

    @staticmethod
    def validate_size(size: Union[None, tuple, list], type_: str):
        if size is None:
            return
        width, height = size
        if width <= 100 or height <= 100:
            raise ValueError(f'Both elements of {type_} must be at least 100: {(width, height)}')


class ValidatorCompileEnv:
    @classmethod
    def validate_duration(cls, duration: str):
        tmp = (f"The value of Duration is invalid. "
               f"It must be a number in the range of 30 to 300, but received: {duration}")
        msg = ["Invalid Duration", tmp]
        if duration.isdigit():
            num = int(duration)
            return 30 <= num <= 300, msg
        return False, msg
