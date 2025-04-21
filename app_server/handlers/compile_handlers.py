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
        toplevel = UIManager.REGISTER.get('compile_toplevel')
        toplevel.destroy()
        btn = UIManager.REGISTER.get('btn_create')
        btn.config(state='normal')

    @staticmethod
    @EventHandlerRegister.registry("compile_btn")
    def click_compile():
        env = os.environ.copy()
        cfg = app_config.compile

        entries = {
            "email_entry": cfg.ENV_EMAIL_USERNAME,
            "entry_password": cfg.ENV_EMAIL_PASSWORD,
            "entry_server": cfg.ENV_EMAIL_SERVER,
            "entry_port": cfg.ENV_EMAIL_PORT,
            "duration_spinbox": cfg.ENV_EMAIL_DURATION,
            "server_ip_entry": cfg.ENV_SERVER_IP,
            "server_port_entry": cfg.ENV_SERVER_PORT
        }
        validators = [(ValidatorCompileEnv.validate_duration, cfg.ENV_EMAIL_DURATION),
                      (ValidatorCompileEnv.validate_port, cfg.ENV_SERVER_PORT)]

        for entry in entries:
            env[entries[entry]] = UIManager.REGISTER.get(entry).get()

        for validator, key in validators:
            ok, msg = validator(env[key])
            if not ok:
                ShowMessageBox.show('show_error', *msg)
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
