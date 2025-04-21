from gui import UIManager


class BaseEventHandler:
    BUTTONS_HEADER = ['btn_screen', 'btn_web_camera', 'btn_destruct', 'btn_file']

    @classmethod
    def change_state_header_buttons(cls, state: str):
        for btn_name in cls.BUTTONS_HEADER:
            btn = UIManager.REGISTER.get(btn_name)
            btn.config(state=state)
