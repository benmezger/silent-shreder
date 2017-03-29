import os
import sys
import ConfigParser
import re
import hashlib

from time import sleep

from core import exceptions
from core.sighandler import SigHandler

# import daemon

SHA512_RE = re.compile(r'^\w{128}$')

def is_valid_hash(_hash):
    if SHA512_RE.match(_hash):
        return True
    return False

class Shreder(object):
    def __init__(self, configfile="config.cfg"):
        if not os.path.exists(os.path.abspath(configfile)):
            raise exceptions.ConfigFileNotFound("Config for 'shreder' was not found")
            sys.exit(1)

        self.config = ConfigParser.RawConfigParser()
        self.config.read(configfile)

        self.debug = self.config.getboolean("shreder", "debug")
        self.max_days = self.config.getfloat("shreder", "max_days")
        self.executable = self.config.get("executable", "program")
        self.executable_args = self.config.get("executable", "args")
        self.executable_hash = self.config.get("executable", "hash")
        self.hash_file = self.config.get("files", "hashes")

        self.hashes = self.set_hashes()

        self._test_executable()

        self.prove_path = self.config.get("files", "proves")
        if not os.path.exists(self.prove_path):
            sys.stdout.write("File prove does not exist. Make sure you create it.\n")

        self.run()

    def run(self):
        signal_handler = SigHandler(self, "info")
        self.info()
        signal_handler.setup()
        self.wait()

    def set_hashes(self):
        """
        Set hashes to an iterator
        """

        if not os.path.exists(os.path.abspath(self.hash_file)):
            raise FileNotFoundError("'%s' was not found. Exiting" % self.hash_file)
            sys.exit(1)

        hashes = []
        with open(os.path.abspath(self.hash_file), "r") as f:
            while True:
                line = f.readline().strip()
                if is_valid_hash(line):
                    hashes.append(line)
                if line == "":
                    break
        return self.__next_hash(hashes)

    def __get_next_prove(self):
        with open(self.prove_path, "r") as f:
            line = f.readline().strip()
            if line:
                return line
        return ""

    def verify_hash(self, msg):
        msg = hashlib.sha512(msg)
        return msg.hexdigest() == self.hashes.next().lower()

    def _test_executable(self):
        """
        Tests if the hash matches the executable and checks if the executable exists
        """

        def is_exe(fpath): return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        # verify hash first
        current_sha = hashlib.sha512()
        with open(self.executable, "rb") as bf:
            while True:
                data = bf.read(65536) # 64kb
                if not data:
                    break
                current_sha.update(data)

        if current_sha.hexdigest() != self.executable_hash:
            sys.stdout.write("Hash of executable '%s' does not match\n" %
                    self.executable)
            sys.exit(1)

        fpath, fname = os.path.split(self.executable)
        if fpath:
            if is_exe(self.executable):
                return True
        return False

    def __next_hash(self, hashlist):
        for _ in hashlist:
            yield _

    def wait(self):
        counter = 10
        while counter > 0:
            sys.stdout.write("Starting execution in %d\n" % counter)
            sys.stdout.write("C^c to stop\n")
            sleep(1)
            counter -= 1

    def info(self):
        sys.stdout.write("########### Shreder information ##########\n")
        sys.stdout.write("Current pid: %*d\n" % (20, os.getpid()))
        sys.stdout.write("Debug enabled: %*d\n" % (18, 1 if self.debug else 0))
        sys.stdout.write("Max days: %*s\n" % (23, self.max_days))
        sys.stdout.write("Shreding executable: %*s\n" % (12, self.executable))
        sys.stdout.write("Executable args %*s\n" % (17, self.executable_args))

if __name__ == "__main__":
    ss = Shreder()
    ss.run()
