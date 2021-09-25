import npyscreen
import curses
import socket
import json
import sys
import os
from . import log_convert
from datetime import datetime

version = "0.8.4"


class ViewForm(npyscreen.Form):
    def __init__(self, name, outer_instance):
        super(ViewForm, self).__init__(name)
        self.outer_instance = outer_instance
        self.keypress_timeout = 10
        self.add_handlers(
            {"^R": self.outer_instance.main, "^Q": self.outer_instance.quit}
        )

    def main(self):
        log = [
            {
                "dx": "NA",
                "mode": "NA",
                "frequency": "NA",
                "time": "No log data found, log an entry!",
                "date": "NA",
                "notes": "NA",
                "tx": "NA",
                "rx": "NA",
            }
        ]
        log = self.outer_instance.log
        displayStr = (
            "time: {} {}, dx: {}, tx RST: {}, rx RST: {}, freq: {}, mode: {}"
        )
        [
            self.add(
                npyscreen.TitleText,
                name=displayStr.format(
                    line.get("time"),
                    line.get("date"),
                    line.get("dx"),
                    line.get("tx"),
                    line.get("rx"),
                    line.get("frequency"),
                    line.get("mode"),
                ),
            )
            for line in log
        ]


class LogForm(npyscreen.Form):
    def __init__(self, name, outer_instance):
        super(LogForm, self).__init__(name)
        self.outer_instance = outer_instance
        self.keypress_timeout = 10
        self.add_handlers(
            {
                "^R": self.outer_instance.main,
                "^W": self.savenow,
                "^L": self.outer_instance.display_logview,
                "^Q": self.outer_instance.quit,
            }
        )
        self.rmode = self.outer_instance.rmode
        self.rfreq = self.outer_instance.rfreq

    def while_waiting(self):
        if self.outer_instance.rigctld:
            self.outer_instance.poll()
            self.freq.value = self.outer_instance.rfreq
            self.mode.value = self.outer_instance.rmode
            self.mode.display()
            self.freq.display()
        else:
            pass

    def main(self):
        self.dx = self.add(npyscreen.TitleText, name="Callsign:")
        self.tx = self.add(npyscreen.TitleText, name="Tx RPT:")
        self.rx = self.add(npyscreen.TitleText, name="Rx RPT:")
        self.notes = self.add(npyscreen.TitleText, name="Notes:")
        self.mode = self.add(
            npyscreen.TitleText,
            name="Mode:",
            value=self.rmode,
            editable=not self.outer_instance.rigctld,
        )
        self.freq = self.add(
            npyscreen.TitleText,
            name="Frequency:",
            value=self.rfreq,
            editable=not self.outer_instance.rigctld,
        )

    def savenow(self, *args):
        self.outer_instance.rmode = self.mode.value.upper()
        self.outer_instance.rfreq = self.freq.value
        self.logit()
        self.outer_instance.main()

    def logit(self, *args):
        try:
            f = open(self.outer_instance.logfile + ".swp", "r")
            try:
                self.outer_instance.log = json.load(f)
            except json.decoder.JSONDecodeError:
                pass
            f.close()
        except IOError:
            f = open(self.outer_instance.logfile + ".swp", "w+")
            f.close()

        if self.mode.value == "CWR":
            self.mode.value = "CW"
        log_entry = {
            "dx": self.dx.value.upper().split(" ")[0],
            "mode": self.mode.value,
            "frequency": self.freq.value,
            "time": datetime.utcnow().strftime("%H%M%S"),
            "date": datetime.utcnow().strftime("%Y%m%d"),
            "notes": " ".join(self.dx.value.split(" ")[1:])
            + " "
            + self.notes.value,
        }
        if len(self.tx.value) > 1:
            log_entry["tx"] = self.tx.value
        else:
            log_entry["tx"] = "599"

        if len(self.rx.value) > 1:
            log_entry["rx"] = self.rx.value
        else:
            log_entry["rx"] = "599"

        self.outer_instance.log.append(log_entry)

        with open(self.outer_instance.logfile + ".swp", "w") as f:
            f.write(json.dumps(self.outer_instance.log))


class Logger(npyscreen.NPSAppManaged):
    def __init__(self, swap, logfile="default.log"):
        self.rigctld = False
        self.logfile = logfile
        self.rmode = ""
        self.rfreq = ""
        if os.path.isfile(self.logfile):
            self.log = log_convert.from_adif(self.logfile)
        else:
            self.log = []
        if swap:
            with open(self.logfile + ".swp", "r") as f:
                log_recovery = json.load(f)
                for item in log_recovery:
                    self.log.append(item)

    def setup_rigctld(self, rigctld_server, rigctld_port):
        self.rigctld_server = rigctld_server
        self.rigctld_port = rigctld_port
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.rigctld_server, self.rigctld_port))
            self.rigctld = True
        except ConnectionRefusedError:
            print("Could not connect to rigctld!")

    def display_logview(self, *args):
        self.F = ViewForm(name="PyLogCq - View", outer_instance=self)
        self.F.main()
        self.F.edit()

    def main(self, *args):
        if self.rigctld:
            self.poll()
        self.F = LogForm(name="PyLogCQ", outer_instance=self)
        self.F.main()
        self.F.edit()
        self.F.savenow()

    def quit(self, *args):
        try:
            self.s.close()
        except AttributeError:
            pass
        with open(self.logfile + ".swp", "w") as f:
            f.write(json.dumps(self.log))
        try:
            with open(self.logfile, "w") as f:
                f.write(
                    log_convert.to_adif(
                        log_convert.load(self.logfile + ".swp")
                    )
                )
            os.remove(self.logfile + ".swp")
        except FileNotFoundError:
            pass
        sys.exit(0)

    def poll(self):
        self.s.sendall(b"m")
        self.rmode = self.s.recv(1024).decode("utf-8").split()[0]
        self.s.sendall(b"f")
        self.rfreq = self.s.recv(1024).decode("utf-8").split()[0]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", help="Output log filename")
    parser.add_argument("-r", "--rigserver", help="Rigctld server address")
    parser.add_argument("-p", "--rigport", help="Rigctld server port")
    parser.add_argument(
        "-v", "--version", action="store_true", help="Print Version"
    )
    args = parser.parse_args()

    if args.version:
        print(version)
        sys.exit(0)

    def chkswp(logfile):
        if os.path.isfile(logfile + ".swp"):
            return True
        else:
            return False

    if args.outfile:
        App = Logger(logfile=args.outfile, swap=chkswp(args.outfile))
    else:
        App = Logger(swap=chkswp("default.log"))

    if args.rigserver and args.rigport:
        rcs = args.rigserver
        rcp = int(args.rigport)
        App.setup_rigctld(rigctld_server=rcs, rigctld_port=rcp)

    App.run()


if __name__ == "__main__":
    main()
