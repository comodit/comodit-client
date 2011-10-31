# coding: utf-8
"""
Environment module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from resource import Resource
from cortex_client.util.json_wrapper import StringFactory

class Environment(Resource):
    """
    Representation of an environment. An environment is enclosed in an
    organization and may contain hosts.
    @see: L{Organization}
    @see: L{Host}
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of change request's state.
        @type json_data: dict, list or String
        """
        super(Environment, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Environment, self).set_api(api)
        self._set_collection(api.get_environment_collection())

    def _show(self, indent = 0):
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Description:", self.get_description()
        print " "*indent, "Organization:", self.get_organization()
        print " "*indent, "Hosts:"
        hosts = self.get_hosts()
        for h in hosts:
            print " "*(indent + 2), h

    def get_organization(self):
        """
        Provides environment's organization.
        @return: The organization's UUID
        @rtype: String
        """
        return self._get_field("organization")

    def set_organization(self, value):
        """
        Sets environment's organization.
        @param value: The organization's UUID
        @type value: String
        """
        return self._set_field("organization", value)

    def get_hosts(self):
        """
        Provides the hosts of this environment. Each host is represented by its
        UUID.
        @return: The list of hosts' UUIDs
        @rtype: list of String
        """
        return self._get_list_field("hosts", StringFactory())

    def set_hosts(self, hosts):
        """
        Sets the hosts of this environment. Each host is represented by its
        UUID.
        @param hosts: The list of hosts' UUIDs
        @type hosts: list of String
        """
        self._set_list_field("hosts", hosts)

    def get_version(self):
        """
        Provides distribution's version.
        @return: Environment's version
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def get_identifier(self):
        """
        Provides this environment's identifier. The identifier is actually a
        path to this environment: org/env where 'org' is the name of environment's
        organization and 'env' environment's name (as returned by get_name).
        @return: Environment's identifier
        @rtype: String
        """
        org_uuid = self.get_organization()
        org = self._api.get_organization_collection().get_resource(org_uuid)
        return org.get_name() + "/" + self.get_name()
