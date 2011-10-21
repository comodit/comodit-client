import os

from cortex_client.util import path
from resource import Resource
from exceptions import PythonApiException
from cortex_client.util.json_wrapper import JsonWrapper

class Parameter(JsonWrapper):
    def __init__(self, json_data = None):
        super(Parameter, self).__init__(json_data)

    def get_key(self):
        return self._get_field("key")

    def set_key(self, key):
        return self._set_field("key", key)

    def get_value(self):
        return self._get_field("value")

    def set_value(self, value):
        return self._set_field("value", value)

    def get_name(self):
        return self._get_field("name")

    def set_name(self, name):
        return self._set_field("name", name)

    def get_version(self):
        return self._get_field("version")

    def show(self, indent = 0):
        print " "*indent, "Key:", self.get_key()
        print " "*indent, "Value:", self.get_value()


class ParameterFactory(object):
    def new_object(self, json_data):
        return Parameter(json_data)


class File(Resource):
    def __init__(self, api = None, json_data = None):
        super(File, self).__init__(json_data)
        self._content_to_upload = None
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(File, self).set_api(api)
        self._set_collection(api.get_file_collection())

    def get_description(self):
        raise NotImplementedError

    def set_description(self, description):
        raise NotImplementedError

    def get_parameters(self):
        return self._get_list_field("parameters", ParameterFactory())

    def set_parameters(self, parameters):
        self._set_list_field("parameters", parameters)

    def add_parameter(self, parameter):
        self._add_to_list_field("parameters", parameter)

    def get_content(self):
        content = self._api.get_client().read(self._resource + "/" +
                                              self.get_uuid(), decode=False)
        return content.read()

    def set_content(self, file_name):
        self._content_to_upload = file_name

    def create(self, force = False):
        if not self._content_to_upload:
            raise PythonApiException("File has no content")

        template_file_name = self._content_to_upload
        if not os.path.exists(template_file_name):
            raise PythonApiException("File "+template_file_name+" does not exist.")

        uuid = self._api.get_client().upload_new_file(template_file_name)

        parameters = {}
        if force: parameters["force"] = "true"

        self.set_json(self._api.get_client().update(self._resource + "/" + uuid + "/_meta",
                                      self.get_json(), parameters))
        self._content_to_upload = None

    def _show(self, indent = 0):
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Parameters:"
        parameters = self.get_parameters()
        for p in parameters:
            p.show(indent + 2)

    def _commit_meta(self, force):
        parameters = {}
        if(force):
            parameters["force"] = "true"
        self.set_json(self._api.get_client().update(self._resource + "/" +
                                                    self.get_uuid() + "/_meta",
                                                    self.get_json(),
                                                    parameters))

    def _commit_content(self, force):
        if(self._content_to_upload):
            self._api.get_client().upload_to_exising_file(self._content_to_upload,
                                                          self.get_uuid())
            self._content_to_upload = None

    def update(self):
        self.set_json(self._client.read(self._resource + "/" + self.get_uuid() +"/_meta"))

    def commit(self, force = False):
        self._commit_content(force)
        self._commit_meta(force)

    def dump(self, dest_folder):
        path.ensure(dest_folder)
        with open(os.path.join(dest_folder, self.get_name()), 'w') as f:
            f.write(self.get_content())
        self.dump_json(os.path.join(dest_folder, "definition.json"))

    def load(self, input_folder):
        self.load_json(os.path.join(input_folder, "definition.json"))
        self.set_content(os.path.join(input_folder, self.get_name()))
