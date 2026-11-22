# Clock-in

A small command-line and GUI time tracker for recording working sessions.
Each session is saved locally in JSON, so the tracker does not require a
server or account.

## How it works

1. Start the tracker when you begin working.
2. The tracker records the current session every five minutes.
3. Stop the tracker when you finish working.
4. Optionally generate an RTF report for a month.

Sessions started and stopped less than 15 minutes apart are merged. Sessions
that cross midnight are split across the two calendar days.

## Requirements

The programs use only the Python standard library. They require Python 3 and
Tkinter for the GUI and report dialogs.

Run commands from the repository directory, because log files are stored in
the `logs/` directory relative to the current working directory.

## Starting a tracker

### Terminal

On Linux or macOS:

```sh
python3 clock_in.py
```

On Windows:

```cmd
python clock_in.py
```

You can also start `clock_in.bat` from Windows.

Stop the terminal tracker with <kbd>Ctrl</kbd>+<kbd>C</kbd>. The current
session is merged into the monthly log before the program exits.

### GUI

```sh
python3 clock_in_gui.py
```

On Windows, `clock_in_gui.py` can also be started by double-clicking it.
Click the **end** button to stop tracking.

## Log files

The tracker creates this structure in the working directory:

```text
logs/
  temp                 # active session while tracking
  YYYY-MM              # monthly working log
  YYYY-MM.backup       # backup of the monthly log
.config                # reporter name and planned hours per day
```

Monthly files contain JSON objects with `from` and `to` timestamps. Backup
files are created before the monthly log is updated.

## Repairing or extending a session

Run these programs only from the repository directory:

- `python3 fix_broken_session.py` closes an incomplete `temp` session using
  its last internally recorded update.
- `python3 extend.py` extends the last session of the current day to the
  current time, but only when the session ended less than three hours ago.

These commands should not be needed after a clean exit.

## Generating a report

```sh
python3 reporter.py
```

The reporter opens dialogs for:

1. entering your name and planned working hours per day;
2. selecting a monthly log under `logs/`; and
3. choosing the destination for an RTF report.

The report includes start and end times, elapsed time, daily totals, and the
difference from the planned daily hours. Sessions longer than six hours are
counted with a mandatory unpaid-break deduction:

- six hours of tracked time counts as six hours;
- later hours count with one hour deducted as a break;
- the deduction applies in repeated six-hour work-plus-break cycles.

## Troubleshooting

- After an interrupted or wrongly closed tracker, run
  `fix_broken_session.py` and verify the monthly log in `logs/`.
- If work was accidentally omitted after a clean exit, run `extend.py`
  promptly. It has a strict three-hour limit.
- A correctly closed session prints its final progress and leaves no active
  `logs/temp` file.
