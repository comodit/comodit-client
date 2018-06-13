class RequestWithMethodMock(object):
    def __init__(self, url, method, headers = {}, data = None):
        self._url = url

    def get_url(self):
        return self._url

    def add_data(self, obj):
        pass

    def add_header(self, key, value):
        pass


class RequestResult(object):
    def __init__(self, string_result):
        self._string_result = string_result

    def __str__(self):
        return self._string_result

    def read(self):
        return self._string_result
