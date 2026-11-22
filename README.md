# Clock-in

A small time tracker with a simple GUI and terminal version. It saves sessions
locally, so you do not need an account or an internet connection.

## Windows: quick start

1. Install Python 3 from [python.org/downloads](https://www.python.org/downloads/).
   During setup, keep the Python Launcher option enabled. The standard
   installer includes Tkinter, which this app uses for its windows.
2. Download this repository as a ZIP using **Code** > **Download ZIP**, then
   extract it to a folder where you can save files (for example, Documents).
   Do not run it from inside the ZIP or from a read-only folder.
3. Open the extracted `clock_in` folder and double-click **`clock_in_gui.bat`**.
   The tracker window will open. Leave its console window open while tracking.
4. Click **Stop tracking** or close the tracker window when you finish. The
   current session is saved automatically.

No packages or command-line setup are required. The `.bat` launchers find the
repository folder automatically and use Python 3 from the Python Launcher or
from PATH.

### Other Windows actions

- Double-click **`reporter.bat`** to create a monthly report. The first time,
  enter your name and planned hours per day, then choose a monthly log in
  `logs` and where to save the report.
- Double-click **`clock_in.bat`** to run the terminal tracker instead. Stop it
  with <kbd>Ctrl</kbd>+<kbd>C</kbd>.
- If the app was interrupted, double-click **`fix_broken_session.bat`** to
  close the incomplete session using its last saved update.
- If you forgot to stop tracking after a clean exit, double-click
  **`extend.bat`** promptly. It can extend today's last session only within
  three hours of its end.

If a launcher says Python 3 cannot be found, install Python 3 and enable the
Python Launcher (or add Python to PATH), then try again.

## Linux and macOS

Run commands from the repository directory, because log files are stored in
the `logs/` directory relative to it.

Start the terminal tracker:

```sh
python3 clock_in.py
```

Or start the GUI:

```sh
python3 clock_in_gui.py
```

Stop the terminal tracker with <kbd>Ctrl</kbd>+<kbd>C</kbd> or click **Stop
tracking** (or close the window) in the GUI.

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

## Log files

The tracker creates this structure in the repository folder:

```text
logs/
  temp                 # active session while tracking
  YYYY-MM              # monthly working log
  YYYY-MM.backup       # backup of the monthly log
.config                # reporter name and planned hours per day
```

Monthly files contain JSON objects with `from` and `to` timestamps. Backup
files are created before the monthly log is updated. Keep the repository
folder, including `logs`, if you want to keep your tracking history.

## Generating a report

On Windows, double-click `reporter.bat`. On Linux or macOS, run:

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
  `fix_broken_session.bat` on Windows or `python3 fix_broken_session.py` on
  Linux/macOS, then verify the monthly log in `logs/`.
- If work was accidentally omitted after a clean exit, run `extend.bat` on
  Windows or `python3 extend.py` on Linux/macOS promptly. It has a strict
  three-hour limit.
- A correctly closed session prints its final progress and leaves no active
  `logs/temp` file.
