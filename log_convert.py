import json

def load(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data

def to_csv(json_log):
    log = json_log
    out = "time, dx, frequency, mode, notes\n"
    for qso in log:
        out += "{}, {}, {}, {}, {}, {}, {}\n".format(qso.get('time'), qso.get('dx'), qso.get('tx'),  qso.get('rx'), so.get('frequency'), qso.get('mode'), qso.get('notes'))
    print(out)


if __name__ == "__main__":
    logfile = load('default.log')
    csv = to_csv(logfile)
