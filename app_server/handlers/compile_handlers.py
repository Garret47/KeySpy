import logging
import os
import subprocess

from gui import UIManager
from utils import EventHandlerRegister, AsyncTkinter, ValidatorCompileEnv, ShowMessageBox
from settings import app_config

logger = logging.getLogger(__name__)


class CompileHandler:
    @staticmethod
    @EventHandlerRegister.registry("close_toplevel")
    def close_toplevel():
        logger.info('Close Toplevel Compile')
        logger.debug(f'Window before close: {list(elem.name for elem in UIManager.WINDOW.children)}')
        toplevel = UIManager.WINDOW.find('compile_toplevel')
        toplevel.builder.widget.destroy()
        toplevel.clear()
        logger.debug(f'Window after close: {list(elem.name for elem in UIManager.WINDOW.children)}')
        btn = UIManager.WINDOW.find('btn_create')
        btn.builder.widget.config(state='normal')

    @staticmethod
    @EventHandlerRegister.registry("compile_btn")
    def click_compile():
        env = os.environ.copy()
        entries = {
            "email_entry": app_config.compile.ENV_EMAIL,
            "entry_password": app_config.compile.ENV_PASSWORD,
            "entry_server": app_config.compile.ENV_SERVER,
            "entry_port": app_config.compile.ENV_PORT,
            "duration_spinbox": app_config.compile.ENV_DURATION
        }
        for entry in entries:
            env[entries[entry]] = UIManager.WINDOW.find(entry).builder.widget.get()

        answer = ValidatorCompileEnv.validate_duration(env[app_config.compile.ENV_DURATION])
        if not answer[0]:
            ShowMessageBox.show('show_error', *answer[1])
            return

        if not app_config.CLIENT_DIR.exists():
            logger.error(f'Client not exists, {app_config.CLIENT_DIR}')
            return

        try:
            subprocess.run(['make', 'clean'], cwd=app_config.CLIENT_DIR, env=env, check=True, capture_output=True)
            result = subprocess.run(['make'], cwd=app_config.CLIENT_DIR, env=env, check=True, capture_output=True)
            logger.info(f'Success, make: {result.stdout.decode()}')
        except subprocess.CalledProcessError as e:
            logger.error('Failed compile, make error')
            logger.debug(f'make output: {e.stderr.decode()}')
        EventHandlerRegister.get('close_toplevel')()
