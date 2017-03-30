import signal
import atexit
import sys

kill_sigs = {
    signal.SIGHUP: "SIGHUP",
    signal.SIGINT: "SIGINT",
    signal.SIGTERM: "SIGTERM",
    signal.SIGQUIT: "SIGQUIT",
    # TODO some signals are missing
    }

class SigHandler(object):
    def __init__(self, cls, funcn, debug=False):
        self.cls = cls
        self.funcn = funcn
        self.debug = debug

    def setup(self):
        sgn = []
        for num in kill_sigs:
            sgn.append(signal.signal(num, self.handler))
            signal.siginterrupt(num, False)

        atexit.register(self.handler, None, None)

    def handler(self, signum, frame):
        if self.debug:
            sys.stdout.write("Running handler..\n")
            return
        getattr(self.cls, self.funcn)()

if __name__ == "__main__":
    pass
