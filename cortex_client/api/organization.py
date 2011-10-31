# coding: utf-8
"""
Organization module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from resource import Resource
from cortex_client.util.json_wrapper import StringFactory

class Organization(Resource):
    """
    An organization. An organization may contain environments.
    
    @see: L{Environment}
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
        super(Organization, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Organization, self).set_api(api)
        self._set_collection(api.get_organization_collection())

    def get_environments(self):
        """
        Provides organization's environments. Environments are added to an
        organization when they are created on cortex server.
        @return: A list of environments UUIDs
        @rtype: list of String
        """
        return self._get_list_field("environments", StringFactory())

    def get_version(self):
        """
        Provides organization's version number.
        @return: The version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def _show(self, indent = 0):
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Description:", self.get_description()
        print " "*indent, "Environments:", self.get_description()
        environments = self.get_environments()
        for e in environments:
            print " "*(indent + 2), e

    def get_identifier(self):
        return self.get_name()
