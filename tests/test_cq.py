import unittest
import sys
import curses
import npyscreen

sys.path.append("./pylogcq")
import pylogcq.cq as cq

npyscreen.TEST_SETTINGS["TEST_INPUT"] = [ch for ch in "test"]
npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
npyscreen.TEST_SETTINGS["CONTINUE_AFTER_TEST_INPUT"] = True


class testSomething(unittest.TestCase):
    App = cq.Logger(logfile="tests/default.log")
    App.run(fork=False)


if __name__ == "__main__":
    unittest.main()
