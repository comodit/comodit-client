class HttpClient(object):
    def __init__(self, endpoint, username, password):
        pass

class Client(object):
    def __init__(self, endpoint, username, password):
        self._http_client = HttpClient(endpoint, username, password)
