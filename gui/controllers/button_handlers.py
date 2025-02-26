from utils import EventHandlerRegister, AsyncTkinter


class ButtonHeaderHandler:
    @staticmethod
    @EventHandlerRegister.registry('main')
    @AsyncTkinter.async_handler
    async def command_main():
        print('Main')

    @staticmethod
    @EventHandlerRegister.registry('info')
    @AsyncTkinter.async_handler
    async def command_info():
        print("Info")

    @staticmethod
    @EventHandlerRegister.registry('create')
    @AsyncTkinter.async_handler
    async def command_create():
        print('Create')

    @staticmethod
    @EventHandlerRegister.registry('screenshot')
    @AsyncTkinter.async_handler
    async def command_screenshot():
        print('Screenshot')

    @staticmethod
    @EventHandlerRegister.registry('web_camera')
    @AsyncTkinter.async_handler
    async def command_web():
        print('Web Camera')

    @staticmethod
    @EventHandlerRegister.registry('self_destruction')
    @AsyncTkinter.async_handler
    async def command_destruct():
        print('Self_Destruction')

    @staticmethod
    @EventHandlerRegister.registry('file_manager')
    @AsyncTkinter.async_handler
    async def command_file():
        print('File Manager')


class ButtonMainHandler:
    @staticmethod
    @EventHandlerRegister.registry('refresh_list')
    @AsyncTkinter.async_handler
    async def command_refresh():
        print('Refresh List')
