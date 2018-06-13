import unittest

from unittest import TestCase

from test.mock.api import Client

from comodit_client.api.collection import Collection, EntityNotFoundException
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.application import Application, ApplicationCollection
from comodit_client.api.distribution import Distribution, DistributionCollection
from comodit_client.api.environment import Environment, EnvironmentCollection
from comodit_client.api.host import Host, HostCollection
from comodit_client.api.organization import Organization, OrganizationCollection, Group, GroupCollection
from comodit_client.api.platform import Platform, PlatformCollection
from comodit_client.api.files import File, FileCollection
from comodit_client.api.settings import Setting, SettingCollection
from comodit_client.api.parameters import Parameter, ParameterCollection
from comodit_client.api.exceptions import PythonApiException

class CollectionTest(TestCase):
    def setUp(self):
        self._client = Client("endpoint", "user", "pass")
        self._collection = Collection(self._client, "url/")

    def tearDown(self):
        pass


    # Add entity tests

    def test_create_success(self):
        # Mock Client.create
        self._client._http_client.create = self._create_successful
        self._expected_entity = "url/"

        json_data = {"test":"value"}
        entity = JsonWrapper(json_data)

        self._collection._create(entity)

    def test_create_failure(self):
        # Mock Client.create
        self._client._http_client.create = self._create_failure
        self._expected_entity = "url/"

        json_data = {"test":"value"}
        entity = JsonWrapper(json_data)

        try:
            self._collection._create(entity)
        except PythonApiException:
            return
        self.assertFalse(True)


    # Get entities tests

    def test_list_success(self):
        # Mock Client.read
        self._read_result = {"count":"3", "items":["a", "b", "c"]}
        self._client._http_client.read = self._read_success
        self._expected_entity = "url/"
        self._collection._new = self._identity

        entities = self._collection.list()

        self.assertEqual(len(entities), 3, "List should contain 3 elements")
        self.assertTrue("a" in entities, "a string should be in list")
        self.assertTrue("b" in entities, "b string should be in list")
        self.assertTrue("c" in entities, "c string should be in list")

    def test_list_failure(self):
        self._client._http_client.read = self._read_failure

        try:
            self._collection.list()
        except PythonApiException:
            return
        self.assertFalse(True)


    # Get entities tests

    def test_get_entity_success(self):
        # Mock Client.read
        self._read_result = "result"
        self._client._http_client.read = self._read_success
        self._expected_entity = "url/a"
        self._collection._new = self._identity

        res = self._collection.get("a")

        self.assertEqual(self._read_result, res)

    def test_get_entity_failure(self):
        self._client._http_client.read = self._read_failure

        try:
            self._collection.get("a")
        except PythonApiException:
            return
        self.assertFalse(True)

    def test_get_entity_not_found(self):
        self._client._http_client.read = self._read_success
        self._expected_entity = ""  # expected entity is 'url/a'

        try:
            self._collection.get("a")
        except EntityNotFoundException:
            return
        self.assertFalse(True)


    # Get entities tests

    def test_get_single_entity_success(self):
        # Mock Client.read
        self._read_result = "result"
        self._client._http_client.read = self._read_success
        self._expected_entity = "url/"
        self._collection._new = self._identity

        res = self._collection.get()

        self.assertEqual(self._read_result, res)

    def test_get_single_entity_failure(self):
        self._client._http_client.read = self._read_failure

        try:
            self._collection.get()
        except PythonApiException:
            return
        self.assertFalse(True)


    # Helpers

    def _create_successful(self, entity, item = None, parameters = {}, decode = True):
        if decode and item is not None:
            return item
        else:
            raise Exception("Unexpected")

    def _create_failure(self, entity, item = None, parameters = {}, decode = True):
        raise ApiException("Error", 0)

    def _read_success(self, entity, parameters = {}, decode = True):
        if entity == self._expected_entity:
            return self._read_result
        else:
            raise ApiException("Not found", 404)

    def _read_failure(self, entity, parameters = {}, decode = True):
        raise ApiException("Error", 0)

    def _identity(self, data):
        return data


class SpecificCollections(TestCase):
    def test_applications(self):
        collection = ApplicationCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Application))

    def test_distributions(self):
        collection = DistributionCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Distribution))

    def test_environments(self):
        collection = EnvironmentCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Environment))

    def test_groups(self):
        collection = GroupCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Group))

    def test_hosts(self):
        collection = HostCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Host))

    def test_organizations(self):
        collection = OrganizationCollection(None)
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Organization))

    def test_platforms(self):
        collection = PlatformCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Platform))

    def test_files(self):
        collection = FileCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, File))

    def test_parameters(self):
        collection = ParameterCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Parameter))

    def test_settings(self):
        collection = SettingCollection(None, "")
        res = collection._new({"name":"name"})
        self.assertTrue(isinstance(res, Setting))


class SubCollections(TestCase):
    def setUp(self):
        self._client = Client("e", "u", "p")
        self._client._http_client.update = self._update
        self._client._http_client.read = self._read

    def test_applications(self):
        collection = ApplicationCollection(self._client, "url/")
        res = collection._new({"name":"app_name"})

        # Parameters
        self._test_parameters(res)

        # Files
        self._test_files(res)

    def test_distributions(self):
        collection = DistributionCollection(self._client, "url/")
        res = collection._new({"name":"dist_name"})

        # Parameters
        self._test_parameters(res)

        # Settings
        self._test_settings(res)

        # Files
        self._test_files(res)

    def test_environments(self):
        collection = EnvironmentCollection(self._client, "url/")
        res = collection._new({"name":"env_name"})

        # Settings
        self._test_settings(res)

        # Hosts
        host_coll = res.hosts()
        host = host_coll._new({"name":"host_name"})
        self._expected_url = "url/" + res.identifier + "/hosts/" + host.identifier
        host.update()

    def test_hosts(self):
        collection = HostCollection(self._client, "url/")
        res = collection._new({"name":"host_name"})

        # Settings
        self._test_settings(res)

        # Application contexts
        app_coll = res.applications()
        self._read_data = {"application":"app_name"}
        context = app_coll._new(self._read_data)
        self._expected_url = "url/" + res.identifier + "/applications/" + context.identifier
        context.refresh()

    def _test_parameters(self, res):
        param_coll = res.parameters()
        param = param_coll._new({"name":"param_name"})
        self._expected_url = "url/" + res.identifier + "/parameters/" + param.identifier
        param.update()

    def _test_settings(self, res):
        set_coll = res.settings()
        setting = set_coll._new({"key":"setting_name"})
        self._expected_url = "url/" + res.identifier + "/settings/" + setting.identifier
        setting.update()

    def _test_files(self, res):
        file_coll = res.files()
        f = file_coll._new({"name":"name"})
        self._expected_url = "url/" + res.identifier + "/files/" + f.identifier
        f.update()

    def _update(self, entity, item = None, parameters = {}, decode = True):
        self.assertEqual(self._expected_url, entity, "Unexpected entity URL " + entity)
        return item

    def _read(self, entity, parameters = {}, decode = True):
        self.assertEqual(self._expected_url, entity, "Unexpected entity URL " + entity)
        return self._read_data


if __name__ == '__main__':
    unittest.main()

