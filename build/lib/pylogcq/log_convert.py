import json


def load(file):
    with open(file, "r") as f:
        data = json.load(f)

    return data


def get_band(frequency):
    frequency = int(frequency)
    if 1800000 <= frequency <= 2000000:
        return "160m"
    elif 3500000 <= frequency <= 4000000:
        return "80m"
    elif 5300000 <= frequency <= 5500000:
        return "60m"
    elif 7000000 <= frequency <= 7300000:
        return "40m"
    elif 10100000 <= frequency <= 10150000:
        return "30m"
    elif 14000000 <= frequency <= 14350000:
        return "20m"
    elif 18068000 <= frequency <= 18168000:
        return "17m"
    elif 21000000 <= frequency <= 21450000:
        return "15m"
    elif 24890000 <= frequency <= 24990000:
        return "12m"
    elif 28000000 <= frequency <= 29700000:
        return "10m"
    elif 50000000 <= frequency <= 54000000:
        return "6m"
    elif 144000000 <= frequency <= 148000000:
        return "2m"
    elif 219000000 <= frequency <= 225000000:
        return "1.25m"
    elif 420000000 <= frequency <= 450000000:
        return "70cm"
    elif 902000000 <= frequency <= 928000000:
        return "33cm"
    else:
        return False


def to_csv(json_log):
    log = json_log
    out = "time, dx, tx, rx, frequency, mode, notes\n"
    for qso in log:
        out += "{}, {}, {}, {}, {}, {}, {}\n".format(
            qso.get("time"),
            qso.get("dx"),
            qso.get("tx"),
            qso.get("rx"),
            qso.get("frequency"),
            qso.get("mode"),
            qso.get("notes"),
        )
    return out


def to_adif(json_log):
    log = json_log
    out = "#ADIF Created by PyLogCQ\n<ADIF_VERS:5>3.1.0 <PROGRAMID:7>PyLogCQ <eoh>\n\n"
    for qso in log:
        freq = qso.get("frequency")
        band = get_band(freq)
        out += "<CALL:{}>{}<FREQ:{}>{}<RST_SENT:{}>{}<RST_RCVD:{}>{}<MODE:{}>{}<COMMENT:{}>{}<TIME_OFF:{}>{}<QSO_DATE:{}>{}<BAND:{}>{}<eor>\n".format(
            len(qso.get("dx")),
            qso.get("dx"),
            len(freq),
            freq,
            len(qso.get("tx")),
            qso.get("tx"),
            len(qso.get("rx")),
            qso.get("rx"),
            len(qso.get("mode")),
            qso.get("mode"),
            len(qso.get("notes")),
            qso.get("notes"),
            len(qso.get("time")),
            qso.get("time"),
            len(qso.get("date")),
            qso.get("date"),
            len(band),
            band,
        )

    return out


def get_ext(filename):
    ext = filename.split(".")[-1]
    return ext


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--outfile", required=True, help="Output log filename"
    )
    parser.add_argument("logfile", help="Input File")
    args = parser.parse_args()

    logfile = load(args.logfile)

    format_map = {"csv": to_csv, "adi": to_adif}

    if get_ext(args.logfile) != "log":
        print("Must be a pylogc .log file")
        quit()

    ext = get_ext(args.outfile)
    conv_func = format_map.get(ext)
    with open(args.outfile, "w") as f:
        f.write(conv_func(logfile))


if __name__ == "__main__":
    main()
