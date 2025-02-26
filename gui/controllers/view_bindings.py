from utils import EventHandlerRegister


class ViewMainBind:
    @staticmethod
    @EventHandlerRegister.registry('click_table')
    def click_tableview_element(event):
        print('Click Table')

