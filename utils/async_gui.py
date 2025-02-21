import tkinter as tk
import _tkinter

import asyncio


class AsyncTkinter:
    @staticmethod
    def get_event_loop():
        return asyncio.get_event_loop_policy().get_event_loop()

    @staticmethod
    async def mainloop(root: tk.Tk):
        while True:
            while root.dooneevent(_tkinter.DONT_WAIT) > 0:
                pass

            try:
                root.winfo_exists()
            except tk.TclError:
                break

            await asyncio.sleep(0.01)

    @staticmethod
    def async_mainloop(root: tk.Tk):
        AsyncTkinter.get_event_loop().run_until_complete(AsyncTkinter.mainloop(root))
