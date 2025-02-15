from .base import Command


class ScreenshotCommand(Command):
    COMMAND = 'create_screenshot'


class WebcamCommand(Command):
    COMMAND = 'start_web_camera'

