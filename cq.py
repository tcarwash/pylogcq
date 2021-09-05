import npyscreen
import socket
import json
import sys
from datetime import datetime

class LogForm(npyscreen.Form):
    def __init__(self, name, outer_instance):
        super(LogForm, self).__init__(name)
        self.outer_instance = outer_instance
        self.keypress_timeout=10

    def while_waiting(self):
        if self.outer_instance.rigctld:
            self.outer_instance.poll()
            self.outer_instance.freq.value = self.outer_instance.rfreq
            self.outer_instance.mode.value = self.outer_instance.rmode
            self.outer_instance.mode.display()
            self.outer_instance.freq.display()
        else:
            pass


class Logger(npyscreen.NPSAppManaged):
    def __init__(self, logfile="default.log"):
        self.rigctld = False
        self.rmode = ""
        self.rfreq = ""
        self.logfile = logfile

    def setup_rigctld(self, rigctld_server, rigctld_port):
        self.rigctld_server = rigctld_server
        self.rigctld_port = rigctld_port
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.rigctld_server, self.rigctld_port))
            self.rigctld = True
        except:
            print('Unable to establish connection')

    def main(self, *args):
        if self.rigctld:
            self.poll()
        #self.F = npyscreen.Form(name = "PyLogCQ")
        self.F = LogForm(name = "PyLogCQ", outer_instance=self)
        self.F.add_handlers({"^R": self.main,
                            "^Q": self.quit,
                            })

        self.dx = self.F.add(npyscreen.TitleText, name = "Callsign:",)
        self.notes = self.F.add(npyscreen.TitleText, name = "Notes:",)
        self.mode = self.F.add(npyscreen.TitleText, name = "Mode:", value = self.rmode, editable=not self.rigctld)
        self.freq = self.F.add(npyscreen.TitleText, name = "Frequency:", value = self.rfreq, editable=not self.rigctld)
        self.F.edit()
        self.mode.value = self.mode.value.upper()
        self.logit()
        self.rmode = self.mode.value
        self.rfreq = self.freq.value
        self.main()

    def quit(self, *args):
        try:
            self.s.close()
        except:
            pass
        sys.exit(0)

    def poll(self):
        self.s.sendall(b'm')
        self.rmode = self.s.recv(1024).decode("utf-8").split()[0]
        self.s.sendall(b'f')
        self.rfreq = self.s.recv(1024).decode("utf-8").split()[0]

    def logit(self):
        log = []
        try:
            f = open(self.logfile, "r")
            try:
                log = json.load(f)
            except json.decoder.JSONDecodeError:
                pass
            f.close()
        except IOError:
            f = open(self.logfile, "w+")
            f.close()

        log.append({"dx": self.dx.value.upper(), 
                    "mode": self.mode.value, 
                    "frequency": self.freq.value,
                    "time": datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"),
                    }) 

        with open(self.logfile, "w") as f:
            f.write(json.dumps(log))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", help="Output log filename")
    parser.add_argument("-r", "--rigserver", help="Rigctld server address")
    parser.add_argument("-p", "--rigport", help="Rigctld server port")
    args = parser.parse_args()

    if args.outfile:
        App = Logger(logfile=args.outfile)
    else:
        App = Logger()

    if args.rigserver and args.rigport:
        rcs = args.rigserver
        rcp = int(args.rigport)
        App.setup_rigctld(rigctld_server=rcs, rigctld_port=rcp)

    App.run()
