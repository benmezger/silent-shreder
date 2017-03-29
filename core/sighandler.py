import signal
import atexit

sig_types = {
        signal.SIGABRT: 'SIGABRT',
        signal.SIGALRM: 'SIGALRM',
        signal.SIGBUS: 'SIGBUS',
        signal.SIGCHLD: 'SIGCHLD',
        signal.SIGCONT: 'SIGCONT',
        signal.SIGFPE: 'SIGFPE',
        signal.SIGHUP: 'SIGHUP',
        signal.SIGILL: 'SIGILL',
        signal.SIGINT: 'SIGINT',
        signal.SIGPIPE: 'SIGPIPE',
        signal.SIGPOLL: 'SIGPOLL',
        signal.SIGPROF: 'SIGPROF',
        signal.SIGQUIT: 'SIGQUIT',
        signal.SIGSEGV: 'SIGSEGV',
        signal.SIGSYS: 'SIGSYS',
        signal.SIGTERM: 'SIGTERM',
        signal.SIGTRAP: 'SIGTRAP',
        signal.SIGTSTP: 'SIGTSTP',
        signal.SIGTTIN: 'SIGTTIN',
        signal.SIGTTOU: 'SIGTTOU',
        signal.SIGURG: 'SIGURG',
        signal.SIGUSR1: 'SIGUSR1',
        signal.SIGUSR2: 'SIGUSR2',
        signal.SIGVTALRM: 'SIGVTALRM',
        signal.SIGXCPU: 'SIGXCPU',
        signal.SIGXFSZ: 'SIGXFSZ',
        }

class SigHandler(object):
    def __init__(self, cls, funcn):
        # self.signals = [s for s in dir(signal) if s.startswith("SIG")]
        self.cls = cls
        self.funcn = funcn

    def setup(self):
        sgn = []
        for num in sig_types:
            sgn.append(signal.signal(num, self.handler))
            signal.siginterrupt(num, False)

    @atexit.register
    def handler(self, signum, frame):
        getattr(self.cls, self.funcn)()

if __name__ == "__main__":
    pass
