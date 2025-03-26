from gui import UIManager
from server import Server


class BaseEventHandler:
    BUTTONS_HEADER = ['btn_screen', 'btn_web_camera', 'btn_destruct', 'btn_file']

    @classmethod
    def change_state_header_buttons(cls, state: str):
        for btn_name in cls.BUTTONS_HEADER:
            btn = UIManager.WINDOW.find(btn_name).builder.widget
            btn.config(state=state)
