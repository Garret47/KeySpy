from ttkbootstrap.dialogs import Messagebox


class ShowMessageBox:
    @staticmethod
    def show(type_: str, title: str,  msg: str):
        show_message = getattr(Messagebox, type_, None)
        if show_message:
            show_message(msg, title)
