from .base import Command


class ScreenshotCommand(Command):
    COMMAND = 'create_screenshot'


class WebcamCommand(Command):
    COMMAND = 'start_web_camera'


class FileCommand(Command):
    COMMAND = 'file_manager'


class InfoCPU(Command):
    COMMAND = "info_cpu"


class InfoMemory(Command):
    COMMAND = "info_memory"


class InfoProcess(Command):
    COMMAND = "info_process"


class InfoDisk(Command):
    COMMAND = "info_disk"


class InfoNetwork(Command):
    COMMAND = "info_network"


class InfoUptime(Command):
    COMMAND = "info_uptime"


class InfoSys(Command):
    COMMAND = "info_sys"
