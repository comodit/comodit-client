# coding: utf-8
"""
API exceptions module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

class PythonApiException(Exception):
    """
    Base class for exceptions raised by API calls.
    """
    def __init__(self, message, cause = None):
        """
        Creates a PythonApiException instance.
        
        @param message: A message
        @type message: String
        @param cause: An exception
        @type cause: Exception
        """
        super(PythonApiException, self).__init__(message)
        self.cause = cause

class NotFoundException(PythonApiException):
    """
    Exception raised when a resource was not found.
    """
    def __init__(self, message):
        """
        Creates a NotFoundException instance.
        
        @param message: A message
        @type message: String
        """
        super(PythonApiException, self).__init__(message)
