import os

from cortex_client.util.json_wrapper import JsonWrapper
from cortex_client.api.exceptions import PythonApiException

import cortex_client.util.path as path

class Resource(JsonWrapper):
    def set_api(self, api):
        self._api = api
        self._client = api.get_client()

    def _set_collection(self, collection):
        self._resource = collection.get_path()
        self._resource_collection = collection

    def get_uuid(self):
        return self._get_field("uuid")

    def set_uuid(self, uuid):
        self._set_field("uuid", uuid)

    def get_name(self):
        return self._get_field("name")

    def set_name(self, name):
        self._set_field("name", name)

    def get_description(self):
        return self._get_field("description")

    def set_description(self, description):
        self._set_field("description", description)

    def update(self):
        self.set_json(self._client.read(self._resource + "/" + self.get_uuid()))

    def commit(self, force = False):
        if(self._client is None):
            raise PythonApiException("API is not set")

        parameters = {}
        if(force):
            parameters["force"] = "true"
        self.set_json(self._client.update(self._resource + "/" +
                                        self.get_uuid(),
                                        self.get_json(),
                                        parameters))

    def create(self):
        if(self._resource_collection is None):
            raise PythonApiException("Collection is not set")

        self._resource_collection.add_resource(self)

    def delete(self):
        if(self._client is None):
            raise PythonApiException("API is not set")

        self.set_json(self._client.delete(self._resource + "/" + self.get_uuid()))

    def show(self, as_json = False, indent = 0):
        if(as_json):
            self.print_json()
        else:
            self._show(indent)

    def get_identifier(self):
        return self.get_name()

    def _show(self, indent = 0):
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Description:", self.get_description()

    def dump(self, dest_folder):
        path.ensure(dest_folder)
        plat_file = os.path.join(dest_folder, "definition.json")
        self.dump_json(plat_file)

    def load(self, input_folder):
        self.load_json(os.path.join(input_folder, "definition.json"))
