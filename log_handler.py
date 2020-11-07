import os
import time
import json
import datetime
import functools


class LogHandler(object):
    def __init__(self):
        self.prep_log_dir()
        self.start = self.get_now()
        self.duration_past = self.get_duration_today_before()

    @classmethod
    def get_sleep_seconds(cls):
        return 60 * 5

    @classmethod
    def get_sleep_print(cls):
        return 60 * 60

    @classmethod
    def sleep(cls):
        time.sleep(cls.get_sleep_seconds())

    @classmethod
    def get_log_format(cls):
        return '%Y-%m-%d %H:%M:%S'

    @classmethod
    def format_datetime(cls, datetime: datetime.datetime):
        return datetime.strftime(cls.get_log_format())

    @classmethod
    def deformat_datetime(cls, string: str):
        return datetime.datetime.strptime(string, cls.get_log_format())

    @classmethod
    def get_log_dir(cls):
        return 'logs'

    @classmethod
    def prep_log_dir(cls):
        if not os.path.isdir(cls.get_log_dir()):
            os.makedirs(cls.get_log_dir())

    @classmethod
    def get_session_name(cls):
        return 'temp'

    @classmethod
    def get_log_session(cls):
        return os.path.join(cls.get_log_dir(), cls.get_session_name())

    def update_session(self, end=None):
        if end is None:
            end = self.get_now()
        assert self.start <= end, 'back to future'
        self.split_overnight(end)
        self.write_month_logs([{
            'from': self.start,
            'to': end
        }], self.get_session_name())
        self.print_progress_today()

    def split_overnight(self, now):
        if self.format_date(self.start) != self.format_date(now):
            start = datetime.datetime(year=now.year,
                                      month=now.month,
                                      day=now.day)
            self.update_session(end=(start - datetime.timedelta(seconds=1)))
            self.merge_session()
            self.start = start
            self.duration_past = now - start

    @classmethod
    def merge_session(cls):
        if os.path.isfile(cls.get_log_session()):
            session = cls.load_month_logs(cls.get_session_name())
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

    @classmethod
    def format_duration(cls, timedelta: datetime.timedelta):
        secs = timedelta.seconds
        return '{:02}:{:02}:{:02}'.format(secs // 3600, (secs % 3600) // 60,
                                          (secs % 60))

    @classmethod
    def format_duration_difference(cls, timedelta_is: datetime.timedelta,
                                   timedelta_should: datetime.timedelta):
        return cls.format_duration(
            timedelta_is - timedelta_should
        ) if timedelta_is >= timedelta_should else '-' + cls.format_duration(
            timedelta_should - timedelta_is)

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

    @classmethod
    def get_duration_today_before(cls):
        formatter = cls.format_date
        now = cls.get_now()
        str_today = formatter(now)
        logs = [
            log for log in cls.load_month_logs(cls.get_month_id(now))
            if formatter(log['from']) == str_today
        ]
        return datetime.timedelta() if len(logs) == 0 else functools.reduce(
            lambda s, d: s + d, (log['to'] - log['from'] for log in logs))

    def print_progress_today(self, force=False):
        now = self.get_now()
        assert self.start <= now, 'back to future'
        duration = self.duration_past + (now - self.start)
        secs_in_hour = duration.seconds % self.get_sleep_print()
        if force or min(secs_in_hour,
                        self.get_sleep_print() -
                        secs_in_hour) < self.get_sleep_seconds() // 2:
            str_date = self.format_date(now)
            str_now = self.format_clocktime(now)
            str_duration = self.format_duration(duration)
            print(f'duration on {str_date} until {str_now} is {str_duration}')
