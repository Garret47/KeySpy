from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GUIConfig:
    FILENAME_MAIN_CONFIG: Path = Path('data/gui/windows/main_window.yaml')
    FILENAME_COMPILE_CONFIG: Path = Path('data/gui/widgets/compile_toplevel/toplevel.yaml')
    FILENAME_SCREEN_CONFIG: Path = Path('data/gui/windows/screen_window.yaml')
    FILENAME_WEB_CONFIG: Path = Path('data/gui/windows/web_window.yaml')


@dataclass
class WidgetNames:
    BUTTON_SCREEN: str = 'btn_screen'
    BUTTON_WEB: str = 'btn_web_camera'
    BUTTON_DESTRUCT: str = 'btn_destruct'
    BUTTON_FILE: str = 'btn_file'
    BUTTON_CREATE: str = 'btn_create'
    TABLE_KEYLOGGERS: str = 'table_keyloggers'
    COMPILE_TOPLEVEL: str = 'compile_toplevel'
    EMAIL_ENTRY: str = 'email_entry'
    ENTRY_PASSWORD: str = 'entry_password'
    ENTRY_SERVER: str = 'entry_server'
    ENTRY_PORT: str = 'entry_port'
    SERVER_IP_ENTRY: str = 'server_ip_entry'
    SERVER_PORT_ENTRY: str = 'server_port_entry'
    DURATION_SPINBOX: str = 'duration_spinbox'
    SCREEN_FRAME_IMG: str = 'screenshot_frame_image'
    LABEL_SCREEN: str = 'label_screenshot'
    BUTTON_SAVE_SCREEN: str = 'btn_save_screenshot'

    def __post_init__(self):
        self.BUTTONS_HEADER_CLIENT: list = [self.BUTTON_SCREEN, self.BUTTON_WEB, self.BUTTON_DESTRUCT, self.BUTTON_FILE]


@dataclass
class CallbackNames:
    CLICK_MAIN: str = 'main'
    CLICK_INFO: str = 'info'
    CLICK_CREATE: str = 'create'
    CLICK_SCREEN: str = 'screenshot'
    CLICK_WEB: str = 'web_camera'
    CLICK_DESTRUCT: str = 'self_destruction'
    CLICK_FILE: str = 'file_manager'
    CLICK_REFRESH: str = 'refresh_list'
    CLICK_TABLE: str = 'click_table'
    CLICK_COMPILE: str = "compile_btn"
    CLICK_CLOSE_TOPLEVEL: str = "close_toplevel"
    CLICK_SAVE_SCREEN: str = 'save_screenshot'


@dataclass
class GUIKeys:
    widget_names: WidgetNames = field(default_factory=WidgetNames)
    callback_names: CallbackNames = field(default_factory=CallbackNames)


@dataclass
class GUI:
    keys: GUIKeys = field(default_factory=GUIKeys)
    config: GUIConfig = field(default_factory=GUIConfig)
