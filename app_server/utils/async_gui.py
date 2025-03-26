import time
import tkinter as tk
import _tkinter
import asyncio
from typing import Callable, List, Tuple


class AsyncTkinter:
    @staticmethod
    def get_event_loop():
        return asyncio.get_event_loop_policy().get_event_loop()

    @staticmethod
    async def mainloop(root: tk.Tk, time_duration: int = None, func: Callable = None):
        current_time = time.time()

        while True:
            while root.dooneevent(_tkinter.DONT_WAIT) > 0:
                pass

            try:
                root.winfo_exists()
            except tk.TclError:
                break

            if func and time_duration:
                if time.time() - current_time >= time_duration:
                    func()
                    current_time = time.time()

            await asyncio.sleep(0.01)

    @staticmethod
    def async_mainloop(root: tk.Tk, time_duration: int = None, func: Callable = None):
        AsyncTkinter.get_event_loop().run_until_complete(AsyncTkinter.mainloop(root, time_duration, func))

    @staticmethod
    def async_handler(async_function: Callable, *args, **kwargs):
        def wrapper(*handler_args):
            AsyncTkinter.get_event_loop().create_task(async_function(*handler_args, *args, **kwargs))
        return wrapper
