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

