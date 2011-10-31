# coding: utf-8
"""
Base collection class module. Cortex server maintains collections of resources.
Resources are listed, retrieved and created through these collections. This
module defines the base resource collection.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from cortex_client.api.exceptions import PythonApiException
from cortex_client.rest.exceptions import ApiException

class ResourceNotFoundException(PythonApiException):
    """
    Exception raised when a resource was not found in a collection.
    """
    def __init__(self, identifier):
        """
        Creates an instance of ResourceNotFoundException.

        @param identifier: The identifier of the resource.
        @type identifier: String
        """
        super(ResourceNotFoundException, self).__init__("Resource not found: "+identifier)

class Collection(object):
    """
    Base resources collection. Cortex server maintains collections of resources.
    Resources are listed, retrieved and created through these collections.
    Most common operations are already implemented by this class. Subclasses
    must at least implement L{_new_resource} and L{get_uuid} methods.
    """

    def __init__(self, resource_path, api):
        """
        Creates an instance of Collection.

        @param resource_path: Path to associated collection on cortex server
        (for example, 'applications' is the relative path to access applications
        collection i.e., if server's API is available at address
        'http://cortex.server.com/api', applications collection is available
        at address 'http://cortex.server.com/api/applications'.
        @type resource_path: String
        @param api: An API access point.
        @type api: L{CortexApi}
        """
        self._resource_path = resource_path
        self._api = api

    def get_path(self):
        """
        Returns the relative path to associated resources collection.

        @return: A relative path
        @rtype: String

        @see: L{__init__}
        """
        return self._resource_path

    def add_resource(self, resource):
        """
        Adds a resource to this collection. A call to this method actually
        creates a new resource on the server. State of the object may be
        updated (in particular, UUID is available as it is associated by
        server).
        
        @param resource: A resource to add to the collection.
        @type resource: L{Resource}
        
        @raise PythonApiException: If the resource could not be created on the
        server.
        """
        try:
            result = self._api.get_client().create(self._resource_path,
                                                   resource.get_json())
        except ApiException, e:
            raise PythonApiException("Could not create resource " +
                                     resource.get_name(), e)
        resource.set_json(result)

    def get_resources(self, parameters = {}):
        """
        Provides the list of resources in associated collection. This list may
        be filtered.
        
        @param parameters: Filtering parameters
        @type parameters: dict of <String,String>
        
        @return: A list of resources
        @rtype: list of L{Resource}
        """
        client = self._api.get_client()
        result = client.read(self._resource_path, parameters)

        resources_list = []
        if(result["count"] != "0"):
            json_list = result["items"]
            for json_res in json_list:
                resources_list.append(self._new_resource(json_res))

        return resources_list

    def _new_resource(self, json_data):
        """
        Instantiates a new resource object. New object's state is set using
        provided JSON data (organized as a dict).

        @param json_data: Initial state of object to instantiate
        @type json_data: C{dict}

        @return: A resource object
        @rtype: L{Resource}
        """
        raise NotImplementedError

    def get_resource(self, uuid):
        """
        Retrieves the resource with given UUID from this collection.
        
        @param uuid: The UUID of the resource to retrieve
        @type uuid: String
        
        @return: A resource object
        @rtype: L{Resource}
        
        @raise PythonApiException: If the resource could not be retrieved from
        server.
        """
        client = self._api.get_client()
        try:
            result = client.read(self._resource_path + "/" + uuid)
        except ApiException, e:
            if e.code == 404:
                raise ResourceNotFoundException(uuid, e)
            else:
                raise PythonApiException("Could not get resource "+uuid, e)
        return self._new_resource(result)

    def get_resource_from_path(self, identifier):
        """
        Retrieves the resource with given identifier from this collection.
        
        @param identifier: The identifier of the resource to retrieve
        @type identifier: String
        
        @return: A resource object
        @rtype: L{Resource}
        
        @raise PythonApiException: If the resource could not be retrieved from
        server.
        """
        try:
            return self.get_resource(self.get_uuid(identifier))
        except ApiException, e:
            if e.code == 404:
                raise ResourceNotFoundException(identifier)
            else:
                raise PythonApiException("Could not get resource "+identifier, e)

    def get_uuid(self, identifier):
        """
        Retrieves the UUID of a resource in this collection with given
        identifier.
        
        @param identifier: The identifier of a resource in this collection.
        @type identifier: String
        
        @return: A UUID
        @rtype: String
        """
        raise NotImplementedError
