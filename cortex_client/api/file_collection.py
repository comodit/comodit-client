# coding: utf-8
"""
File collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from file import File

class FileCollection(Collection):
    """
    File collection. Collection of the files available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new FileCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(FileCollection, self).__init__("files", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new File object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{File}
        """

        return File(self._api, json_data)

    def get_uuid(self, name):
        """
        Retrieves the UUID of a file given its identifier. A file only uniquely
        defined by its UUID.

        @param name: The name of a host
        @type name: String
        """
        return name

    def get_resource(self, uuid):
        """
        Retrieves the file with given UUID from this collection.

        @param uuid: The UUID of the resource to retrieve
        @type uuid: String
        
        @return: A resource object
        @rtype: L{Resource}
        
        @raise PythonApiException: If the resource could not be retrieved from
        server.
        """
        result = self._api.get_client().read(self._resource_path + "/" + uuid + "/_meta")
        return self._new_resource(result)
