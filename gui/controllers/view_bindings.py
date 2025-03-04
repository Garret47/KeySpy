from utils import EventHandlerRegister, AsyncTkinter
from .manager import UIManager


class ViewMainBind:
    @staticmethod
    @EventHandlerRegister.registry('click_table')
    def click_tableview_element(event):
        buttons_header = ['btn_screen', 'btn_web_camera', 'btn_destruct', 'btn_file']
        ui_manager = UIManager()
        for btn_name in buttons_header:
            btn = ui_manager.window.find(btn_name).builder.widget
            btn.config(state='normal')
