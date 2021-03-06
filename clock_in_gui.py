import tkinter
import multiprocessing

from log_handler import LogHandler

LogHandler.merge_session()
LogHandler.backup()
handler = LogHandler()


def close():
    thread_update.terminate()
    handler.update_session()
    LogHandler.merge_session()
    handler.print_progress_today(force=True)
    base_window.destroy()


def func_update():
    while True:
        handler.update_session()
        handler.print_progress_today(force=False)
        LogHandler.sleep()


if __name__ == '__main__':
    base_window = tkinter.Tk()
    base_window.title('clock-in')

    thread_update = multiprocessing.Process(target=func_update)
    thread_update.start()

    tkinter.Button(base_window, text='end', height=5, width=80,
                   command=close).pack()

    tkinter.mainloop()
