import ConfigParser
import sys
import os
from json import loads as jloads
import random

import daemon

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

class Delete(object):
    def __init__(self, default_config=True):
        if default_config == True:
            self.default_config = "./config.cfg"
        else:
            if os.path.exists(default_config):
                self.default_config = default_config
            else:
                raise ConfigFileNotFound("Config for 'auto-delete was not found'")
                sys.exit(1)
        
        config = ConfigParser.ConfigParser(default_config)
        config.readfd(open(default_confg))
        
        if config.getboolean("auto-delete", "use_overwrite"):
            self.program = None
            self.args = None
        else:
            self.program = config.get("deletion", "program")
            self.args = config.get("deletion", "args")
            if _test_executable() == False:
                raise ExecutableError("Program %s is not executable or could not be found." % self.cmd)
                sys.exit(1)
        
        self.fcheck = config.get("delection", "fcheck")
        self.include = jloads(config.get("files", "include"))
        self.debug = config.getboolean("auto-delete", "debug")

        if debug:
            sys.stdout.write("Warning: debug is enabled\n")
            for f in self.include:
                if not os.path.exists(f):
                    sys.stdout.write("%s does not exist\n" % f)
                else:
                    sys.stdout.write("Found path %s\n" % f) 
    
    def _execute_wiper(self, fpath): # TODO, fix this crap
        sys.stdout.write("Executing custom wiper - Warning: security issue\n")
        random.seed()
        pass

    def execute(self):
        for f in self.include:
            if self.debug:
                sys.stdout.write("Deleting %s\n" % f)
            if self.program:
                self._execute_program(f)
            else:
                self._execute_wiper(f)

    def _test_executable(self):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(self.program)
        if fpath:
            if is_exe(self.program):
                return True
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, self.program)
                if is_exe(exe_file):
                    return True
        return False
