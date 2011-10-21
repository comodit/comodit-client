from cortex_client.control.exceptions import ControllerException

class SyncException(ControllerException):
    def __init__(self, msg):
        ControllerException.__init__(self, msg)