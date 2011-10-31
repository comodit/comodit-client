# coding: utf-8
"""
Environment collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from environment import Environment

class EnvironmentCollection(Collection):
    """
    Environment collection. Collection of the environments available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new EnvironmentCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(EnvironmentCollection, self).__init__("environments", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new Environment object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{Environment}
        """

        return Environment(self._api, json_data)

    def get_uuid(self, path):
        """
        Retrieves the UUID of an environment given its name.

        @param path: The name of an environment
        @type path: String
        """
        return self._api.get_directory().get_environment_uuid_from_path(path)
