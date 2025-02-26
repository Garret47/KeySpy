from utils import EventHandlerRegister


class ButtonHeaderHandler:
    @staticmethod
    @EventHandlerRegister.registry('main')
    def command_main():
        print('Main')

    @staticmethod
    @EventHandlerRegister.registry('info')
    def command_info():
        print("Info")

    @staticmethod
    @EventHandlerRegister.registry('create')
    def command_create():
        print('Create')

    @staticmethod
    @EventHandlerRegister.registry('screenshot')
    def command_screenshot():
        print('Screenshot')

    @staticmethod
    @EventHandlerRegister.registry('web_camera')
    def command_web():
        print('Web Camera')

    @staticmethod
    @EventHandlerRegister.registry('self_destruction')
    def command_destruct():
        print('Self_Destruction')

    @staticmethod
    @EventHandlerRegister.registry('file_manager')
    def command_file():
        print('File Manager')


class ButtonMainHandler:
    @staticmethod
    @EventHandlerRegister.registry('refresh_list')
    def command_refresh():
        print('Refresh List')
