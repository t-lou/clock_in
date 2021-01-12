# lite version of ProjectTimeManager for clock in

Open computer -> start clock-in -> start working -> end clock-in -> stop working.
This way should be more convenient for counting the working time, than writing the time down with paper or Excel.

# Programs

- clock_in.py

Main program for Linux terminal and Windows CMD. Progress is printed; end with ctrl-c.

- clock_in.bat

Windows batch file for starting the program. Progress is printed; end with ctrl-c.

- clock_in_gui.py

Starter with GUI button for ending. This can be started with Linux terminal, Windows CMD or double-click in Windows File Browser.
Progress is printed; end with button.

- extend.py

When the program is ended but you continue to work, for example when you do paper work without computer or a colleague asks for a favour when you planed to leave, this program will extend the last working session until now.

- fix_broken_session.py

When the program is wrongly stopped: terminal closed, process kill, computer power empty or program not closed in Windows after several hours, this script ends the last working session to the last internally logged time point (every 5 min). This has no effect when the last working session is closed correctly.

- reporter.py

Open one log file (for one month) and generate report in RTF. If one working session is longer than 6 hours, a break until 1 hour will be counted.

# Attention

This was not tested and used in Linux. In Windows, clock_in.py in CMD, clock_in.bat and clock_in_gui.py all have the closure problem.
After some hours of use, ctrl-c and end button may not be received correctly. The reason is unknown, sometimes clicking on the CMD helps.
After closing the program, it is recommanded to check the log file or execute "fix_broken_session.py" and "extend.py" in sequence.

When the program is correctly closed, the progress (current time and duration) is printed again without extra error message.