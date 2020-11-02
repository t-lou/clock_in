import os
import datetime
import json
import tkinter
import tkinter.filedialog
from log_handler import LogHandler


def select_log():
    tkinter.Tk().withdraw()
    filename = tkinter.filedialog.askopenfilename(
        initialdir=LogHandler.get_log_dir())
    assert bool(filename), 'file not selected'
    logs = LogHandler.load_month_logs(os.path.basename(filename))
    LogHandler.check_logs(logs)
    return logs


def select_output():
    tkinter.Tk().withdraw()
    ext = '.rtf'
    filename = tkinter.filedialog.asksaveasfilename(
        initialdir='.', filetypes=((ext, ext), ))
    assert bool(filename), 'file not selected'
    if not filename.endswith(ext):
        filename += ext
    return filename


def report(path: str, logs: list, name: str, should_hour_per_day: float):
    assert len(logs) > 0, 'empty log'
    done = set()
    timedelta_should_per_day = datetime.timedelta(hours=should_hour_per_day)
    total_duration = LogHandler.count_total_duration(logs)
    duration_in_day = LogHandler.count_duration_per_day(logs)

    def format_cell(content: str):
        return f'\\intbl {content} \\cell '

    def format_row(log):
        date_id = LogHandler.get_date_id(log['from'])

        date = date_id if date_id not in done else ''
        start = LogHandler.format_clocktime(log['from'])
        end = LogHandler.format_clocktime(log['to'])
        elapsed = format_duration(log['to'] - log['from'])
        elapsed_in_day = format_duration(
            duration_in_day[date_id]) if date_id not in done else ''
        delta = format_duration_difference(
            duration_in_day[date_id],
            timedelta_should_per_day) if date_id not in done else ''
        content = os.linesep.join([
            format_cell(elem)
            for elem in [date, start, end, elapsed, elapsed_in_day, delta]
        ])
        done.add(date_id)
        return content

    def format_duration(timedelta):
        secs = timedelta.seconds
        return '{:02}:{:02}:{:02}'.format(secs // 3600, (secs % 3600) // 60,
                                          (secs % 60))

    def format_duration_difference(timedelta_is, timedelta_should):
        return format_duration(
            timedelta_is - timedelta_should
        ) if timedelta_is >= timedelta_should else '-' + format_duration(
            timedelta_should - timedelta_is)

    cells = [f'\\cellx{r}' for r in (800, 1800, 2800, 3800, 4900, 6000)]
    table_head = '\\trowd\\pard\\trqc ' + ' '.join(cells)

    with open(path, 'w') as fs:
        fs.write('{\\rtf1\\ansi\\deff0' + os.linesep)
        fs.write('\\qr \\sb300 {\\loch %s}' %
                 (LogHandler.format_date(LogHandler.get_now()), ) + os.linesep)
        fs.write('\\par\\pard\\sb300\\plain {\\loch Dear %s,}' % (name, ) +
                 os.linesep)
        fs.write(
            '\\par\\pard\\sb300\\sa300\\plain {\\loch your working time in %s from %s to %s is as follows:}'
            % (LogHandler.get_month_id(logs[0]['from']),
               LogHandler.format_date(logs[0]['from']),
               LogHandler.format_date(logs[-1]['from'])) + os.linesep)
        fs.write('\\par\\pard\\sb100\\sa100\\qc' + os.linesep)
        fs.write(
            table_head.replace(
                '\\cellx', '\\clbrdrt\\brdrth\\clbrdrb\\brdrs\\cellx').replace(
                    '\\pard', '') + os.linesep)
        fs.write(''.join([
            f'\\intbl {title} \\cell '
            for title in ['Date', 'Start', 'End', 'Elapsed', 'Sum', 'Change']
        ]) + '\\row' + os.linesep)

        for id_log, log in enumerate(logs, 1):
            fs.write((table_head if id_log < len(logs) else table_head.replace(
                '\\cellx', '\\clbrdrb\\brdrth\\cellx')) + os.linesep)
            fs.write(format_row(log) + os.linesep)
            fs.write('\\row\\pard' + os.linesep)

        fs.write(
            '\\par\\pard\\sb100\\plain {\\loch The total working time for the %d days with time tracking is %s, the balance for this period is %s (with %s planned per day).}'
            % (len(duration_in_day), format_duration(total_duration),
               format_duration_difference(
                   total_duration,
                   datetime.timedelta(
                       hours=(should_hour_per_day * len(duration_in_day)))),
               format_duration(timedelta_should_per_day)) + os.linesep)

        fs.write('\\par\\pard\\sb300\\plain {\\loch Sincerely yours}' +
                 os.linesep)
        fs.write('\\par\\pard\\sb300\\plain {\\loch time_tracker}' +
                 os.linesep)
        fs.write('}' + os.linesep)


def get_config():
    path = '.config'
    if not os.path.isfile(path) or set(json.loads(
            open(path).read()).keys()) != set(['name', 'hours']):
        width = 20
        height = 2
        root = tkinter.Tk()
        tkinter.Label(
            root,
            text='name',
            width=width,
            height=height,
            justify=tkinter.LEFT).pack(side=tkinter.TOP)
        text_field_name = tkinter.Text(root, height=height, width=width)
        text_field_name.pack(side=tkinter.TOP)
        tkinter.Label(
            root,
            text='hours per day',
            width=width,
            height=height,
            justify=tkinter.LEFT).pack(side=tkinter.TOP)
        text_field_dura = tkinter.Text(root, height=height, width=width)
        text_field_dura.pack(side=tkinter.TOP)

        def exec(event):
            name = text_field_name.get('1.0', tkinter.END).strip()
            hours = text_field_dura.get('1.0', tkinter.END).strip()
            with open(path, 'w') as fs:
                fs.write(json.dumps({'name': name, 'hours': float(hours)}))
            root.destroy()

        root.bind('<Return>', exec)

        text_field_name.focus()
        tkinter.mainloop()

    return json.loads(open(path).read())


if __name__ == '__main__':
    config = get_config()
    logs = select_log()
    path = select_output()
    name = config['name']
    should_hour_per_day = config['hours']
    report(path, logs, name, should_hour_per_day)
