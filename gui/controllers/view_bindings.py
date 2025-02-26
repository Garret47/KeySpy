from utils import EventHandlerRegister, AsyncTkinter


class ViewMainBind:
    @staticmethod
    @EventHandlerRegister.registry('click_table')
    @AsyncTkinter.async_handler
    async def click_tableview_element(event):
        print(event)
        print('Click Table')

