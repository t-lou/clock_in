import threading
import tkinter

from log_handler import LogHandler


if __name__ == "__main__":
    LogHandler.merge_session()
    LogHandler.backup()
    handler = LogHandler()
    stop_update = threading.Event()

    def close():
        stop_update.set()
        thread_update.join(timeout=LogHandler.get_sleep_seconds() + 1)
        handler.update_session()
        LogHandler.merge_session()
        handler.print_progress_today(force=True)
        base_window.destroy()

    def func_update():
        while not stop_update.is_set():
            handler.update_session()
            handler.print_progress_today(force=False)
            stop_update.wait(LogHandler.get_sleep_seconds())

    base_window = tkinter.Tk()
    base_window.title("clock-in")

    thread_update = threading.Thread(target=func_update, daemon=True)
    thread_update.start()

    tkinter.Label(
        base_window, text="Tracking is active. Stop tracking when you finish."
    ).pack(padx=24, pady=(20, 10))
    tkinter.Button(
        base_window, text="Stop tracking", height=2, width=24, command=close
    ).pack(padx=24, pady=(0, 20))

    base_window.protocol("WM_DELETE_WINDOW", close)
    tkinter.mainloop()
