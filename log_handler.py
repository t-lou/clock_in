import os
import time
import json
import datetime
import shutil
import functools

# after how many hours one has to make take a pause, non-positive to deactivate
kHoursMandatoryPause = 6


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

    def sleep_to_hour(self, now=datetime.datetime):
        duration_secs = (self.duration_past + (now - self.start)).seconds
        left_secs = (duration_secs // 3600) * 3600 + 3600 - duration_secs
        if 0 < left_secs < self.get_sleep_seconds():
            time.sleep(left_secs)

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
    def get_log_path(cls, filename: str):
        return os.path.join(cls.get_log_dir(), filename)

    @classmethod
    def get_log_session(cls):
        return cls.get_log_path(cls.get_session_name())

    def update_session(self, end=None):
        if end is None:
            end = self.get_now()
        assert self.start <= end, 'back to future'
        self.split_overnight(end)
        self.sleep_to_hour(end)
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
    def merge_logs(cls, logs1: list, logs2: list):
        cls.check_logs(logs1)
        cls.check_logs(logs2)
        if len(logs1) == 0:
            assert len(logs2) > 0, 'both logs emtpy'
            return logs2

        merged = logs1[:]
        if bool(logs2):
            assert logs1[-1]['to'] <= logs2[0]['from'], 'two logs inconsistent'
            delta = logs2[0]['from'] - logs1[-1]['to']
            if delta.days == 0 and delta.seconds < 15 * 60:
                merged[-1]['to'] = logs2[0]['to']
            else:
                merged += logs2
        return merged

    @classmethod
    def merge_session(cls):
        if os.path.isfile(cls.get_log_session()):
            session = cls.load_month_logs(cls.get_session_name())
            assert len(session) == 1, 'temp must have length 1'
            datetime = session[0]['from']
            logs = cls.merge_logs(
                cls.load_month_logs(cls.get_month_id(datetime)), session)
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
        path = cls.get_log_path(month_id)
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
        str_log = json.dumps(
            [{key: cls.format_datetime(log[key])
              for key in ('from', 'to')} for log in logs],
            indent=' ')
        with open(cls.get_log_path(month_id), 'w') as fs:
            fs.write(str_log)

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
        return '{:02}:{:02}:{:02}'.format(secs // 3600 + timedelta.days * 24,
                                          (secs % 3600) // 60, (secs % 60))

    @classmethod
    def format_duration_difference(cls, timedelta_is: datetime.timedelta,
                                   timedelta_should: datetime.timedelta):
        return cls.format_duration(
            timedelta_is - timedelta_should
        ) if timedelta_is >= timedelta_should else '-' + cls.format_duration(
            timedelta_should - timedelta_is)

    @staticmethod
    def check_logs(logs: list):
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
        is_pause_mandatory = kHoursMandatoryPause is not None and kHoursMandatoryPause > 0
        if is_pause_mandatory:
            secs_without_pause = int(kHoursMandatoryPause * 3600.0)
            secs_with_pause = secs_without_pause + 3600
        for log in logs:
            secs = (log['to'] - log['from']).seconds
            if is_pause_mandatory:
                secs = (secs // secs_with_pause) * secs_without_pause + (
                    secs % secs_with_pause)
            duration_in_day[LogHandler.get_date_id(
                log['from'])] += datetime.timedelta(seconds=secs)
        return duration_in_day

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

    @classmethod
    def extend_until_now(cls):
        allowed_interval_secs = 3 * 60 * 60
        now = cls.get_now()
        str_today = cls.format_date(now)
        month_id = cls.get_month_id(now)
        full_logs = cls.load_month_logs(month_id)
        logs = [
            log for log in full_logs
            if cls.format_date(log['from']) == str_today
        ]
        assert bool(logs), 'no session today'
        last_end = logs[-1]['to']
        assert last_end < now, 'still in last session r u kidding?'
        assert (now - last_end).seconds < allowed_interval_secs, 'too late'
        full_logs[-1]['to'] = now
        cls.write_month_logs(full_logs, month_id)

    @classmethod
    def get_backup_name(cls, filename: str):
        return filename + '.backup'

    @classmethod
    def check_backup(cls, month_id: str):
        logs_original = cls.load_month_logs(month_id)
        logs_backup = cls.load_month_logs(cls.get_backup_name(month_id))
        assert len(logs_original) >= len(logs_backup), 'wrong backup'
        for i in range(min(len(logs_backup), len(logs_original) - 1)):
            assert logs_original[i] == logs_backup[i], 'wrong backup session'

    @classmethod
    def backup(cls, month_id: str = None):
        if month_id is None:
            month_id = cls.get_month_id(cls.get_now())
        if os.path.isfile(cls.get_log_path(month_id)):
            cls.check_backup(month_id)
            shutil.copy(cls.get_log_path(month_id),
                        cls.get_log_path(cls.get_backup_name(month_id)))
