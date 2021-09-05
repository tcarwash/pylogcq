import npyscreen
import socket
import json
from datetime import datetime

class Logger(npyscreen.NPSApp):
    def __init__(self, logfile="default.log"):
        self.rigctld = False
        self.rmode = ""
        self.rfreq = ""
        self.logfile = logfile

    def setup_rigctld(self, rigctld_server, rigctld_port):
        self.rigctld_server = rigctld_server
        self.rigctld_port = rigctld_port
        self.rigctld = True

    def main(self):
        if self.rigctld:
            self.poll()
        self.F = npyscreen.Form(name = "PylogCQ",)
        self.dx = self.F.add(npyscreen.TitleText, name = "Callsign:",)
        self.notes = self.F.add(npyscreen.TitleText, name = "Notes:",)
        self.mode = self.F.add(npyscreen.TitleText, name = "Mode:", value = self.rmode, editable=not self.rigctld)
        self.freq = self.F.add(npyscreen.TitleText, name = "Frequency:", value = self.rfreq, editable=not self.rigctld)
        self.F.edit()
        self.logit()
        self.main()

    def poll(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.rigctld_server, self.rigctld_port))
        s.sendall(b'm')
        self.rmode = s.recv(1024).decode("utf-8").split()[0]
        s.sendall(b'f')
        self.rfreq = s.recv(1024).decode("utf-8").split()[0]

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
