from log_handler import LogHandler


def main():
    LogHandler.merge_session()
    handler = LogHandler()
    try:
        while True:
            handler.update_session()
            LogHandler.sleep()
    except:
        handler.update_session()
        LogHandler.merge_session()
        handler.print_progress_today(force=True)


if __name__ == '__main__':
    main()
