import time
from log_handler import LogHandler


def main():
    LogHandler.merge_session()
    handler = LogHandler()
    try:
        while True:
            handler.update_session()
            time.sleep(60 * 5)
    except:
        handler.update_session()
        LogHandler.merge_session()


if __name__ == '__main__':
    main()
