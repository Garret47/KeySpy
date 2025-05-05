from settings import app_config
from gui import UIManager


class BaseEventHandler:
    @classmethod
    def change_state_header_buttons(cls, state: str):
        for btn_name in app_config.gui.keys.widget_names.BUTTONS_HEADER:
            btn = UIManager.REGISTER.get(btn_name)
            btn.config(state=state)

    @classmethod
    def change_state_client_buttons(cls, state: str):
        for btn_name in app_config.gui.keys.widget_names.BUTTONS_CLIENT:
            btn = UIManager.REGISTER.get(btn_name)
            if btn:
                btn.config(state=state)
