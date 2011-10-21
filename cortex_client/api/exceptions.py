class PythonApiException(Exception):
    def __init__(self, message, cause = None):
        super(PythonApiException, self).__init__(message)
        self.cause = cause

class NotFoundException(PythonApiException):
    def __init__(self, message):
        super(PythonApiException, self).__init__(message)
