import ConfigParser
import sys
import os
import subprocess
import socket
from datetime import datetime
import struct
from json import loads as jloads

import daemon
from OpenSSL import SSL

class ExecutableError(Exception):
    def __init__(self, message, errors):
        super(ExecutableError, self).__init__(message)
        self.error = errors
        self.message = message

class ConfigFileNotFound(Exception):
    def __init__(self, message, errors):
        super(ConfigFileNotFound, self).__init__(message)
        self.error = errors
        self.message = message

class AutoDelete(object):
    def __init__(self, default_config=True):
        if default_config == True:
            self.default_config = "config.cfg"
        else:
            if os.path.exists(default_config):
                self.default_config = default_config
            else:
                raise ConfigFileNotFound("Config for 'auto-delete was not found'")
                sys.exit(1)
        
        config = ConfigParser.RawConfigParser()
        config.read(self.default_config)
        
        self.program = config.get("deletion", "program")
        self.args = config.get("deletion", "args")
        if self._test_executable() == False:
            raise ExecutableError("Program %s is not executable or could not be found." % self.program, "")
            sys.exit(1)
        
        self.tls_host = config.get("auto-delete", "tls_host")
        self.tls_port = config.getint("auto-delete", "tls_port")
        self.max_days = config.getint("auto-delete", "max_days") 
        self.fcheck = config.get("files", "fcheck")
        self.include = jloads(config.get("files", "include"))
        self.debug = config.getboolean("auto-delete", "debug")

        if self.debug:
            sys.stdout.write("Warning: debug is enabled\n")
            for f in self.include:
                if not os.path.exists(f):
                    sys.stdout.write("%s does not exist\n" % f)
                else:
                    sys.stdout.write("Found path %s\n" % f) 
    
    def _query_date(self, host, port): # TODO: verify SSL safely.
        host = socket.getaddrinfo(host, port)[0][4][0] # get the IP
        context = SSL.Context(SSL.TLSv1_2_METHOD)
        
        sock = socket.socket()
        sock = SSL.Connection(context, sock)
        sock.connect((host, port))
        sock.do_handshake()

        return datetime.fromtimestamp(struct.unpack('>L', sock.server_random()[:4])[0])

    def cmp_dates(self):
        if not os.path.exists(self.fcheck):
            return True
        mtime = datetime.fromtimestamp(os.path.getmtime(self.fcheck))
        now = self._query_date(self.tls_host, self.tls_port)
        
        delta = now - mtime
        if delta.days < self.max_days: # days have passed, delete it
            return False 
        return True

    def _destroy(self, fpath):
        fpath = os.path.realpath(fpath)
        destroy_cmd = self.program + " " + self.args + " " + fpath
        proc = subprocess.Popen(destroy_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, shell=True)
        
        _stdout, _stderr = proc.communicate("")
        _stdout = str(_stdout).strip()
        
        return _stdout

    def execute(self):
        for f in self.include:
            if self.debug:
                sys.stdout.write("Deleting %s\n" % f)
            self._destroy(f)

    def _test_executable(self):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(self.program)
        if fpath:
            if is_exe(self.program):
                return True
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, self.program.strip('"'))
                if is_exe(exe_file):
                    self.program = exe_file
                    return True
        return False
    
    def run(self):
        while True:
            print "running"
            changed = self.cmp_dates()
            if changed:
                self.execute()
            
if __name__ == "__main__":
    ad = AutoDelete()
    ad.run()
    with daemon.DaemonContext():
        ad.run()
