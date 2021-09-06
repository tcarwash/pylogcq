import json

def load(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data

def to_csv(json_log):
    log = json_log
    out = "time, dx, frequency, mode\n"
    for qso in log:
        out += "{}, {}, {}, {}\n".format(qso.get('time'), qso.get('dx'), qso.get('frequency'), qso.get('mode'))
    print(out)


if __name__ == "__main__":
    logfile = load('default.log')
    csv = to_csv(logfile)
