# coding: utf-8
"""
Provides the classes related to environment entity: L{Environment}
and L{EnvironmentCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from .host import HostCollection
from comodit_client.api.settings import HasSettings
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.exceptions import PythonApiException
from comodit_client.api.audit import AuditLogCollection
from comodit_client.api.notificationLog import NotificationLogCollection
from comodit_client.api.agentLog import AgentLogCollection
from comodit_client.api.otherLog import OtherLogCollection
from comodit_client.api.group import GroupCollection
from comodit_client.api.group import GroupOrganizationTreeCollection



class EnvironmentCollection(Collection):
    """
    Collection of environments. An environment collection is owned by an
    L{Organization}.
    """

    def _new(self, json_data = None):
        return Environment(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new environment object.

        @param name: The name of new environment.
        @type name: string
        @param description: The description of new environment.
        @type description: string
        @rtype: L{Environment}
        """

        env = self._new()
        env.name = name
        env.description = description
        return env

    def create(self, name, description = ""):
        """
        Creates a remote environment entity and returns associated local
        object.

        @param name: The name of new environment.
        @type name: string
        @param description: The description of new environment.
        @type description: string
        @rtype: L{Environment}
        """

        env = self.new(name, description)
        env.create()
        return env


class Environment(HasSettings):
    """
    Environment entity representation. An environment defines a group of hosts
    sharing a common property, for example geographical location.
    An environment may have settings, these settings being available to all
    hosts in this environment.

    An environment entity owns 3 collections:
      - settings (L{Setting})
      - hosts (L{Host})
      - audit logs (L{AuditLog})
    """

    @property
    def organization(self):
        """
        The name of the organization owning this environment.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def hosts_f(self):
        """
        The names of the hosts in this environment.

        @rtype: list of string
        """

        return self._get_list_field("hosts")

    def hosts(self):
        """
        Instantiates the collection of hosts associated to this environment.

        @return: The collection of hosts associated to this environment.
        @rtype: L{HostCollection}
        """

        return HostCollection(self.client, self.url + "hosts/")

    def get_host(self, name):
        """
        Fetches a host of this environment given its name.

        @param name: The name of the host.
        @type name: string
        @rtype: L{Host}
        """

        return self.hosts().get(name)

    def clone(self, clone_name):
        """
        Requests the cloning of remote entity. Clone will have given name.
        This name should not already be in use. Note that the hosts in cloned
        environment will have a clone with same name in cloned environment.
        Cloned hosts will all be in DEFINED state (see L{Host}).

        @param clone_name: The name of the clone.
        @type clone_name: string
        @return: The representation of environment's clone.
        @rtype: L{Environment}
        """

        try:
            result = self._http_client.update(self.url + "_clone", parameters = {"name": clone_name})
            return Environment(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone environment: " + e.message)

    def audit_logs(self):
        """
        Instantiates the collection of audit logs associated to this environment.
        The audit log refer to the environment itself as well as to all hosts
        and their contexts.

        @return: The collection of audit logs associated to this environment.
        @rtype: L{AuditLogCollection}
        """

        return AuditLogCollection(self.client, self.url + "audit/")
    
    def notification_logs(self):
        """
        Instantiates the collection of notification logs associated to this environment.
        The notification log refer to the environment itself as well as to all hosts
        and their contexts.

        @return: The collection of notification logs associated to this environment.
        @rtype: L{NotificationLogCollection}
        """

        return NotificationLogCollection(self.client, self.url + "notification/")

    def agent_logs(self):
        """
        Instantiates the collection of agent logs associated to this environment.
        The agent log refer to the environment itself as well as to all hosts
        and their contexts.

        @return: The collection of agent logs associated to this environment.
        @rtype: L{AgentLogCollection}
        """

        return AgentLogCollection(self.client, self.url + "agent/")

    def other_logs(self):
        """
        Instantiates the collection of other logs associated to this environment.
        The other log refer to the environment itself as well as to all hosts
        and their contexts.

        @return: The collection of other logs associated to this environment.
        @rtype: L{OtherLogCollection}
        """

        return OtherLogCollection(self.client, self.url + "other/")

    def groups(self):
        """
        Instantiates the collection of groups associated to this environment.

        @return: The collection of groups associated to this environment.
        @rtype: L{GroupCollection}
        """
        print (self.url)
        return GroupCollection(self.client, self.url + "groups/")

    def groupsTree(self):
        """
        Get all groups defined in all environment

        @return: The collection of groups associated to this environment.
        @rtype: L{GroupEnvironmentTreeCollection}
        """
        return GroupOrganizationTreeCollection(self.client, self.url + "groups").get("/tree")


    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Organization:", self.organization)
        print(" "*indent, "Hosts:")
        hosts = self.hosts_f
        for h in hosts:
            print(" "*(indent + 2), h)
