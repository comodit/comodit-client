# coding: utf-8
"""
Application collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from application import Application

class ApplicationCollection(Collection):
    """
    Application collection. Collection of the applications available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new ApplicationCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(ApplicationCollection, self).__init__("applications", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new Application object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{Application}
        """
        return Application(self._api, json_data)

    def get_uuid(self, name):
        """
        Retrieves the UUID of an application given its name.

        @param name: The name of an application
        @type name: String
        """
        return self._api.get_directory().get_application_uuid(name)
