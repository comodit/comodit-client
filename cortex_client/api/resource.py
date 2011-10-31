# coding: utf-8
"""
Base resource class module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

import os

from cortex_client.util.json_wrapper import JsonWrapper
from cortex_client.api.exceptions import PythonApiException

import cortex_client.util.path as path

class Resource(JsonWrapper):
    """
    Represents a resource managed by a cortex server. An instance of this class
    may be seen as a proxy to a resource managed by a cortex-server. Note that
    alterations of a Resource instance's state are not automatically committed
    to the server. A call to L{commit} actually updates the state of the object
    on the server. In addition, this class may be instantiated in order to
    create a new resource on the server. In this case, the resource does not yet
    exist on the server and, once the state of the local object is complete,
    must be explicitly created by a call to L{create}.
    """

    def set_api(self, api):
        """
        Sets the cortex server access point.

        @param api: An access point.
        @type api: L{CortexApi}
        """
        self._api = api
        self._client = api.get_client()

    def _set_collection(self, collection):
        """
        Sets the collection this resource is associated to.

        @param collection: A collection
        @type collection: L{Collection}
        """
        self._resource = collection.get_path()
        self._resource_collection = collection

    def get_uuid(self):
        """
        Provides the UUID of this resource or None if it is not yet set.

        @return: A UUID
        @rtype: String
        """
        return self._get_field("uuid")

    def set_uuid(self, uuid):
        """
        Sets the UUID of this resource.

        @param uuid: The new UUID
        @type uuid: String

        @warning: The UUID of a resource is generally set by the server.
        Only use this method if you know what you do.
        """
        self._set_field("uuid", uuid)

    def get_name(self):
        """
        Provides the name of this resource or None if it is not yet set.
        
        @return: The name of this resource.
        @rtype: String
        """
        return self._get_field("name")

    def set_name(self, name):
        """
        Sets the name of this resource.

        @param name: The new name
        @type name: String
        """
        self._set_field("name", name)

    def get_description(self):
        """
        Provides the description for this resource or None if it is not yet set.

        @return: The description of this resource.
        @rtype: String
        """
        return self._get_field("description")

    def set_description(self, description):
        """
        Sets the description of this resource.

        @param description: The new description
        @type description: String
        """
        self._set_field("description", description)

    def update(self):
        """
        Replaces the state of this object with state retrieved from server.

        @raise PythonApiException: If server access point is not set.
        """
        if(self._client is None):
            raise PythonApiException("API is not set")

        self.set_json(self._client.read(self._resource + "/" + self.get_uuid()))

    def commit(self, force = False):
        """
        Updates the state of the resource on the server with state of local
        object.

        @param force: Update is forced
        @type force: Boolean

        @raise PythonApiException: If server access point is not set.
        """
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
        """
        Creates a new resource on the server using this object's state for
        initialization.

        @raise PythonApiException: If server access point is not set.
        """
        if(self._resource_collection is None):
            raise PythonApiException("Collection is not set")

        self._resource_collection.add_resource(self)

    def delete(self):
        """
        Deletes associated resource on the server.

        @raise PythonApiException: If server access point is not set.
        """
        if(self._client is None):
            raise PythonApiException("API is not set")

        self.set_json(self._client.delete(self._resource + "/" + self.get_uuid()))

    def show(self, as_json = False, indent = 0):
        """
        Prints this resource's state to standard output. The state may be
        indented. It can also be displayed using JSON format.

        @param as_json: If True, resource's state is displayed in JSON format.
        Otherwise, it is displayed in a more user-friendly way.
        @type as_json: Boolean
        @param indent: The number of spaces to put in front of each displayed
        line (only if as_json is False).
        @type indent: Integer
        """
        if(as_json):
            self.print_json()
        else:
            self._show(indent)

    def get_identifier(self):
        """
        Provides the identifier of this resource in its collection.
        The identifier may be used with directory service to retrieve the UUID
        of this resource.

        @return: The identifier of this resource.
        @rtype: String
        """
        return self.get_name()

    def _show(self, indent = 0):
        """
        Prints this resource's state to standard output in a user-friendly way.
        
        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Description:", self.get_description()

    def dump(self, dest_folder):
        """
        Dumps the state of this object in given folder. Several files may be
        created in destination folder, as well as sub-folders.
        
        @param dest_folder: The path to destination folder
        @type dest_folder: String
        """
        path.ensure(dest_folder)
        plat_file = os.path.join(dest_folder, "definition.json")
        self.dump_json(plat_file)

    def load(self, input_folder):
        """
        Loads the state of this object from files contained by given folder.
        
        @param input_folder: Path to source folder
        @type input_folder: String
        """
        self.load_json(os.path.join(input_folder, "definition.json"))

