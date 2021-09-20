# PyLogCQ
## A simple curses based log for ham radio use
PyLogCQ is my attempt at a simple, easy to use and hopefully useful terminal based logging program for amateur (ham) radio use.

PyLogCQ will read Frequency and Mode from a [Hamlib](https://github.com/Hamlib/Hamlib) `rigctld` server. PyLogCQ assumes everyone is 599 unless you tell it otherwise, leaving you to make QSOs and enter callsigns/notes.

If PyLogCQ is not being used with `rigctld` PyLogCQ will retain frequency and mode between logged QSOs unless changed, assuming you haven't changed mode/frequency unless you tell it you have.

### Installation
`pip install pylogcq-tcarwash`

**Suggested** Create an alias for `cq='cq -o desired-log.log'` *add `-r` and `-p` if you have a rigctld server you always use*
### Usage

```
Usage: cq [-h] [-o OUTFILE] [-r RIGSERVER] [-p RIGPORT]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Output log filename
  -r RIGSERVER, --rigserver RIGSERVER
                        Rigctld server address
  -p RIGPORT, --rigport RIGPORT
                        Rigctld server port
```

### Keyboard Shortcuts
| Command | Description |
|---|---|
| Ctrl-Q | Quit |
| Ctrl-W | Write QSO to log |
| Ctrl-R | Clear current view and start over at log entry form |
| Ctrl-L | Open log viewer|
