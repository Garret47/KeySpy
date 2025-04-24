from settings import app_config
from gui import UIManager


class BaseEventHandler:
    @classmethod
    def change_state_header_buttons(cls, state: str):
        for btn_name in app_config.gui.keys.widget_names.BUTTONS_HEADER_CLIENT:
            btn = UIManager.REGISTER.get(btn_name)
            btn.config(state=state)
