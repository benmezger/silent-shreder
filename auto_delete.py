import os
import sys
import ConfigParser
import re
import hashlib
import tempfile
import errno
import subprocess
import json
import shutil

from time import sleep

from core import exceptions
from core.sighandler import SigHandler
from core.counter import ClockSpawner

# import daemon

SHA512_RE = re.compile(r'^\w{128}$')

def is_valid_hash(_hash):
    if SHA512_RE.match(_hash):
        return True
    return False

def is_root():
    return os.getuid() == 0

def can_write_fs(path):
    try:
        test_file = tempfile.TemporaryFile(dir=path)
        test_file.close()
        assert os.access(path, os.W_OK)
    except OSError as err:
        if err.errno == errno.EACCES:
            return False
    return True

class Shreder(object):
    def __init__(self, configfile="config.cfg"):
        if not os.path.exists(os.path.abspath(configfile)):
            raise exceptions.ConfigFileNotFound("Config for 'shreder' was not found")
            sys.exit(1)

        self.config = ConfigParser.RawConfigParser()
        self.config.read(configfile)

        self.debug = self.config.getboolean("shreder", "debug")
        self.max_hours = self.config.getfloat("shreder", "max_hours")
        self.executable = self.config.get("executable", "program")
        self.executable_args = self.config.get("executable", "args")
        self.executable_hash = self.config.get("executable", "hash")
        self.hash_file = self.config.get("files", "hashes")
        self.files = json.loads(self.config.get("files", "include"))

        if is_root():
            sys.stdout.write("Running as a root user. Create a different user \
                    and run it again.\n")
            sys.exit(1)

        for _file in self.files:
            if not can_write_fs(_file):
                sys.stdout.write("'%s' doesn't have permission for writting" % _file)
                sys.exit(1)

        self.hashes = self.set_hashes()

        self._test_executable()

        self.prove_path = self.config.get("files", "proves")
        if not os.path.exists(self.prove_path):
            sys.stdout.write("File prove does not exist. Make sure you create it.\n")

        self.run()

    def run(self):
        signal_handler = SigHandler(self, "shred", debug=self.debug)
        self.info()
        signal_handler.setup()
        self.wait()

        clock = ClockSpawner(self.max_hours, self, self.shred)
        clock.run()

    def shred(self):
        for _f in self.files:
            if self.debug:
                sys.stdout.write("Running %s %s %s" % (self.executable,
                                                       self.executable_args, _f))
            else:
                subprocess.call([self.executable, self.executable_args, _f])

    def secure_delete(path, passes=1):
        with open(path, "ba+") as f:
            _len = f.tell()
            for i in range(passes):
                f.seek(0)
                if self.debug:
                    sys.stdout.write("Running os.urandom (passes = %d) into \
                            '%s'\n" % (passes, path))
                else:
                    f.write(os.urandom(_len))
        if self.debug:
            sys.stdout.write("Running rmtree %s\n" % path)
            return
        shutil.rmtree(path)

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
        sys.stdout.write("Max hours: %*s\n" % (23, self.max_hours))
        sys.stdout.write("Shreding executable: %*s\n" % (12, self.executable))
        sys.stdout.write("Executable args %*s\n" % (17, self.executable_args))

if __name__ == "__main__":
    ss = Shreder()
    ss.run()
