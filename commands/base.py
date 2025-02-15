import abc
import logging

from settings import app_config

logger = logging.getLogger(app_config.LOGGER_NAME)


class CommandError(Exception):
    pass


class Meta(abc.ABCMeta, type):
    def __new__(cls, name, bases, dct):
        if not any(issubclass(base, abc.ABC) for base in bases):
            command = dct.get('COMMAND')
            if not (isinstance(command, str) and command):
                logger.exception(f'Error command - {dct}')
                raise CommandError('Command not supported')
        return super(Meta, cls).__new__(cls, name, bases, dct)

    def __str__(cls):
        if hasattr(cls, 'COMMAND'):
            return f'{cls.COMMAND}'
        return super(Meta, cls).__str__()


class Command(abc.ABC, metaclass=Meta):
    COMMAND: str
