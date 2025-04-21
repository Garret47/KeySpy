from dataclasses import dataclass, field
from pathlib import Path


class AppConfigError(Exception):
    pass


@dataclass
class CompileConfig:
    ENV_EMAIL_USERNAME: str = "EMAIL_USERNAME"
    ENV_EMAIL_PASSWORD: str = "EMAIL_PASSWORD"
    ENV_EMAIL_PORT: str = "EMAIL_PORT"
    ENV_EMAIL_SERVER: str = "EMAIL_SERVER"
    ENV_EMAIL_DURATION: str = "DURATION"
    ENV_SERVER_IP: str = "SERVER_IP"
    ENV_SERVER_PORT: str = "SERVER_PORT_STR"


@dataclass
class GUIConfig:
    FILENAME_MAIN_CONFIG: Path = Path('data/gui/windows/main_window.yaml')
    FILENAME_COMPILE_CONFIG: Path = Path('data/gui/widgets/compile_toplevel/toplevel.yaml')
    FILENAME_SCREEN_CONFIG: Path = Path('data/gui/windows/screen_window.yaml')
    FILENAME_WEB_CONFIG: Path = Path('data/gui/windows/web_window.yaml')


@dataclass
class AppConfig:
    FILE_LOGGING_CONFIG: Path = Path('data/logging.yaml')
    CLIENT_DIR: Path = Path('../app_client/')
    gui: GUIConfig = field(default_factory=GUIConfig)
    compile: CompileConfig = field(default_factory=CompileConfig)


app_config = AppConfig()
