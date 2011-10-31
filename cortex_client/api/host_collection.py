# coding: utf-8
"""
Host collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection

class HostCollection(Collection):
    """
    Host collection. Collection of the hosts available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new HostCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(HostCollection, self).__init__("hosts", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new Host object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{Host}
        """

        from host import Host
        return Host(self._api, json_data)

    def get_uuid(self, path):
        """
        Retrieves the UUID of a host given its path. The path of a host is:
        Org/Env/host where Org is the name of an organization, Env the name
        of an environment of organization Org and host the name of a host.

        @param path: The name of a path
        @type path: String
        """
        return self._api.get_directory().get_host_uuid_from_path(path)
