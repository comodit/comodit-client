import unittest, json

from comodit_client.rest.client import HttpClient
from comodit_client.rest.exceptions import ApiException
from test.mock.urllib_mocks import RequestWithMethodMock, RequestResult


class ClientTest(unittest.TestCase):
    def setUp(self):
        self._url = "url"
        self._params = ""
        self._api = "http://localhost/api"
        self._user = "user"
        self._pass = "pass"
        self._token = None
        self._headers = None
        self._urlopen_result = None

        self._client = HttpClient(self._api, self._user, self._pass, self._token)

        # Mock some Client methods
        self._client._new_request = self._new_request
        self._client._new_request_with_data = self._new_request_with_data

    def tearDown(self):
        pass


    # Create tests

    def test_create_success(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        result = self._client.create(self._url, item = data)
        self.assertEqual(data, result, "Wrong result returned")

    def test_create_success_w_params(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)
        self._params = "?param2=value2&param1=value1"

        result = self._client.create(self._url, item = data, parameters = {"param1":"value1", "param2":"value2"})
        self.assertEqual(data, result, "Wrong result returned")

    def test_create_wrong_url(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        try:
            self._client.create(self._url + "x", item = data)
        except:
            return
        self.assertFalse(True)

    def test_create_success_wo_decode(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        result = self._client.create(self._url, item = data, parameters = {}, decode = False)
        self.assertEqual(data, json.load(result), "Wrong result returned")

    def test_create_failure_urlopen(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_failure

        try:
            self._client.create(self._url, item = {})
        except ApiException:
            return
        self.assertFalse(True)


    # Delete tests

    def test_delete_success(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        self._client.delete(self._url)

    def test_delete_wrong_url(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        try:
            self._client.delete(self._url + "x")
        except:
            return
        self.assertFalse(True)

    def test_delete_failure_urlopen(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_failure

        try:
            self._client.delete(self._url)
        except ApiException:
            return
        self.assertFalse(True)


    # Read tests

    def test_read_success(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        result = self._client.read(self._url)
        self.assertEqual(data, result, "Wrong result returned")

    def test_read_wrong_url(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        try:
            self._client.read(self._url + "x")
        except:
            return
        self.assertFalse(True)

    def test_read_failure_urlopen(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_failure

        try:
            self._client.read(self._url)
        except ApiException:
            return
        self.assertFalse(True)


    # Update tests

    def test_update_success(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        result = self._client.update(self._url, item = data)
        self.assertEqual(data, result, "Wrong result returned")

    def test_update_wrong_url(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        try:
            self._client.update(self._url + "x", item = data)
        except:
            return
        self.assertFalse(True)

    def test_update_success_wo_decode(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_success
        data = {"test":"value"}
        self._urlopen_result = json.dumps(data)

        result = self._client.update(self._url, item = data, parameters = {}, decode = False)
        self.assertEqual(data, json.load(result), "Wrong result returned")

    def test_update_failure_urlopen(self):
        # Mock _urlopen
        self._client._urlopen = self._urlopen_failure

        try:
            self._client.update(self._url, item = {})
        except ApiException:
            return
        self.assertFalse(True)


    # Helpers

    def _new_request(self, url, m):
        req = RequestWithMethodMock(url, method = m, headers = self._headers)
        return req

    def _new_request_with_data(self, url, m, d):
        req = RequestWithMethodMock(url, method = m, headers = self._headers, data = d)
        return req

    def _urlopen_success(self, request):
        if request.get_url() == self._api + "/" + self._url + self._params:
            return RequestResult(self._urlopen_result)
        else:
            raise Exception()

    def _urlopen_failure(self, request):
        raise ApiException("message", 404)

if __name__ == '__main__':
    unittest.main()
