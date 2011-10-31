# coding: utf-8
"""
File module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

import os

from cortex_client.util import path
from resource import Resource
from exceptions import PythonApiException
from cortex_client.util.json_wrapper import JsonWrapper

class Parameter(JsonWrapper):
    """
    A template's parameter. A parameter is reprensented by a key, a default value
    and a name. A version is also associated to the parameter by the server.
    """
    def __init__(self, json_data = None):
        super(Parameter, self).__init__(json_data)

    def get_key(self):
        """
        Provides parameter's key.
        @return: The key
        @rtype: String
        """
        return self._get_field("key")

    def set_key(self, key):
        """
        Sets parameter's key.
        @param key: The key
        @type key: String
        """
        return self._set_field("key", key)

    def get_value(self):
        """
        Provides parameter's default value.
        @return: The default value
        @rtype: String
        """
        return self._get_field("value")

    def set_value(self, value):
        """
        Sets parameter's default value.
        @param value: The default value
        @type value: String
        """
        return self._set_field("value", value)

    def get_name(self):
        """
        Provides parameter's name.
        @return: The name
        @rtype: String
        """
        return self._get_field("name")

    def set_name(self, name):
        """
        Sets parameter's name.
        @param name: The name
        @type name: String
        """
        return self._set_field("name", name)

    def get_version(self):
        """
        Provides parameter's version number.
        @return: The version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def show(self, indent = 0):
        """
        Prints parameter's state to standard output in a user-friendly way.
        
        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "Key:", self.get_key()
        print " "*indent, "Value:", self.get_value()


class ParameterFactory(object):
    """
    File parameter factory.
    
    @see: L{Parameter}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a L{Parameter} object using given state.
        
        @param json_data: A quasi-JSON representation of a Package instance's state.
        @type json_data: String, dict or list
        
        @return: A parameter
        @rtype: L{Parameter}
        """
        return Parameter(json_data)


class File(Resource):
    """
    A file template. A template is the representation of a parametrized file.
    A template may be rendered after values are given to its parameters (see
    L{RenderingService}).
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
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
        """
        Provides the list of parameters associated to this template.
        @return: The list of parameters
        @rtype: list of L{Parameter}
        """
        return self._get_list_field("parameters", ParameterFactory())

    def set_parameters(self, parameters):
        """
        Sets the list of parameters associated to this template.
        @param parameters: The list of parameters
        @type parameters: list of L{Parameter}
        """
        self._set_list_field("parameters", parameters)

    def add_parameter(self, parameter):
        """
        Adds a parameter to the list of parameters associated to this template.
        @param parameter: The parameter
        @type parameter: L{Parameter}
        """
        self._add_to_list_field("parameters", parameter)

    def get_content(self):
        """
        Provides template's content. Content may be read from a file object.
        @return: A file object to template's content
        @rtype: A file object
        """
        content = self._api.get_client().read(self._resource + "/" +
                                              self.get_uuid(), decode = False)
        return content

    def set_content(self, file_name):
        """
        Sets template's content. Content is read from a given file. Note that
        templates content is not directly updated on cortex server. Commit must
        be called for this.
        @param file_name: The path to new content's file
        @rtype: String
        """
        self._content_to_upload = file_name

    def create(self, force = False):
        if not self._content_to_upload:
            raise PythonApiException("File has no content")

        template_file_name = self._content_to_upload
        if not os.path.exists(template_file_name):
            raise PythonApiException("File " + template_file_name + " does not exist.")

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
        """
        Commits template's meta-data only.
        @param force: If true, force parameter is used
        @type force: Boolean
        """
        parameters = {}
        if(force):
            parameters["force"] = "true"
        self.set_json(self._api.get_client().update(self._resource + "/" +
                                                    self.get_uuid() + "/_meta",
                                                    self.get_json(),
                                                    parameters))

    def _commit_content(self, force):
        """
        Commits template's content only.
        @param force: If true, force parameter is used
        @type force: Boolean
        """
        if(self._content_to_upload):
            self._api.get_client().upload_to_exising_file(self._content_to_upload,
                                                          self.get_uuid())
            self._content_to_upload = None

    def update(self):
        self.set_json(self._client.read(self._resource + "/" + self.get_uuid() + "/_meta"))

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
