import npyscreen
import socket
import json
from datetime import datetime

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
        self.F = npyscreen.Form(name = "PylogCQ")
        self.F.add_handlers({"^R": self.main,
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
