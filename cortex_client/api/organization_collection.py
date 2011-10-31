# coding: utf-8
"""
Organization collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from organization import Organization

class OrganizationCollection(Collection):
    """
    Organization collection. Collection of the organizations available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new OrganizationCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(OrganizationCollection, self).__init__("organizations", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new Organization object with given state.

        @param json_data: A quasi-JSON representation of organization's state.
        @type json_data: dict

        @see: L{Organization}
        """

        return Organization(self._api, json_data)

    def get_uuid(self, path):
        """
        Retrieves the UUID of an organization given its name.

        @param path: The name of an organization
        @type path: String
        """
        return self._api.get_directory().get_organization_uuid(path)
