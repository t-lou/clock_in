import os
import json
import datetime
import functools

kFormat = '%Y-%m-%d %H:%M:%S'


class LogHandler(object):
    def __init__(self):
        self.prep_log_dir()
        self.now = self.get_now()

    @classmethod
    def format_datetime(cls, datetime: datetime.datetime):
        return datetime.strftime(kFormat)

    @classmethod
    def deformat_datetime(cls, string: str):
        return datetime.datetime.strptime(string, kFormat)

    @classmethod
    def get_log_dir(cls):
        return 'logs'

    @classmethod
    def prep_log_dir(cls):
        if not os.path.isdir(cls.get_log_dir()):
            os.makedirs(cls.get_log_dir())

    @classmethod
    def get_log_session(cls):
        return os.path.join(cls.get_log_dir(), 'temp')

    def update_session(self):
        self.write_month_logs([{
            'from': self.now,
            'to': self.get_now()
        }], 'temp')

    @classmethod
    def merge_session(cls):
        if os.path.isfile(cls.get_log_session()):
            session = cls.load_month_logs('temp')
            assert len(session) == 1, 'temp must have length 1'
            datetime = session[0]['from']
            logs = cls.load_month_logs(cls.get_month_id(datetime)) + session
            cls.write_month_logs(logs)
            os.remove(cls.get_log_session())

    @classmethod
    def get_now(cls):
        return datetime.datetime.now()

    @classmethod
    def load_month_logs(cls, month_id=None):
        if month_id is None:
            month_id = cls.get_month_now()
        content = []
        path = os.path.join(cls.get_log_dir(), month_id)
        if os.path.isfile(path):
            with open(path) as fs:
                content = [{
                    key: cls.deformat_datetime(session[key])
                    for key in ('from', 'to')
                } for session in json.loads(fs.read())]
        return content

    @classmethod
    def write_month_logs(cls, logs: list, month_id=None):
        cls.check_logs(logs)
        if month_id is None:
            month_id = cls.get_month_now()
        with open(os.path.join(cls.get_log_dir(), month_id), 'w') as fs:
            fs.write(
                json.dumps([{
                    key: cls.format_datetime(log[key])
                    for key in ('from', 'to')
                } for log in logs]))

    @classmethod
    def format_clocktime(cls, date: datetime.datetime):
        return date.strftime('%H:%M:%S')

    @classmethod
    def format_date(cls, date: datetime.datetime):
        return date.strftime('%Y-%m-%d')

    @classmethod
    def get_date_id(cls, date: datetime.datetime):
        return date.strftime('%m-%d')

    @classmethod
    def get_month_id(cls, date: datetime.datetime):
        return date.strftime('%Y-%m')

    @classmethod
    def get_month_now(cls):
        return cls.get_month_id(cls.get_now())

    @staticmethod
    def check_logs(logs):
        last = None
        for log in logs:
            assert last is None or last <= log['from'], 'sessions inconsistant'
            assert log['from'] <= log['to'], f'inconsistent in session {log}'
            last = log['to']

    @classmethod
    def count_duration_per_day(cls, logs: list):
        duration_in_day = {
            LogHandler.get_date_id(log['from']): datetime.timedelta()
            for log in logs
        }
        for log in logs:
            duration_in_day[LogHandler.get_date_id(
                log['from'])] += log['to'] - log['from']
        return duration_in_day

    @staticmethod
    def count_total_duration(logs):
        return functools.reduce(lambda s, d: s + d,
                                (log['to'] - log['from'] for log in logs))
