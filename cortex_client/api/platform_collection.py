# coding: utf-8
"""
Platform collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from platform import Platform

class PlatformCollection(Collection):
    """
    Platform collection. Collection of the platforms available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new PlatformCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(PlatformCollection, self).__init__("platforms", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new Platform object with given state.

        @param json_data: A quasi-JSON representation of Platform's state.
        @type json_data: dict

        @see: L{Platform}
        """

        return Platform(self._api, json_data)

    def get_uuid(self, name):
        """
        Retrieves the UUID of a platform given its name.

        @param name: The name of an application
        @type name: String
        """
        return self._api.get_directory().get_platform_uuid(name)
