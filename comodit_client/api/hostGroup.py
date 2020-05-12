# coding: utf-8
"""
Provides the classes related to hostgroup entity: L{HostGroup}
and L{HostGroupCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper


class HostGroupCollection(Collection):
    """
    Collection of host group. A host group collection is owned by an organization
    L{Organization}.
    """
    def _new(self, json_data = None):
        return HostGroup(self, json_data)

    def new(self, json_data):
        """
        Instantiates a new host group object.

        @rtype: L{HostGroup}
        """

        hostGroup = self._new(json_data)
        return hostGroup

    def create(self):
        """
        Creates a remote hostGroup entity and returns associated local
        object.

        @rtype: L{HostGroup}
        """

        hostGroup = self.new()
        hostGroup.create()
        return hostGroup


class HostGroup(Entity):
    """
    HostGroup entity representation. A host group is a group of host.

    """
    @property
    def organization(self):
        """
        The name of the organization owning this orchestration.

        @rtype: string
        """
        return self._get_field("organization")


    @property
    def name(self):
        """
        The name of the hostGroup

        @rtype: string
        """
        return self._get_field("name")

    @property
    def description(self):
        """
        The description of the hostGroup

        @rtype: string
        """
        return self._get_field("description")

    @property
    def ordered_host(self):
        """
        List of host's in group

        @rtype: list of ordered hosts L{HostQueue}
        """

        return self._get_list_field("hosts", lambda x: OrderedHost(x))

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Hosts:")

        #sort by position
        self.ordered_host.sort(key=lambda x: x.position)
        for h in self.ordered_host:
            h._show(indent + 2)

class OrderedHostGroup(JsonWrapper):
    @property
    def position(self):
        """
        the position of hostgroups

        @rtype: string
        """
        return self._get_field("position")


    @property
    def hostgroup(self):
        """
        Hostgroups is a container of ordered hosts

        @rtype: string
        """
        return HostGroup(None, self._get_field("hostGroup"));

    def _show(self, indent = 0):
        print(" "*indent, "Position:", self.position)
        self.hostgroup._show(indent+2)


class OrderedHost(JsonWrapper):

    @property
    def organization(self):
        """
        The organization name

        @rtype: string
        """
        return self._get_field("organization")

    @property
    def environment(self):
        """
        The environment name

        @rtype: string
        """
        return self._get_field("environment")

    @property
    def host(self):
        """
        The host name

        @rtype: string
        """
        return self._get_field("host")

    @property
    def canonical_name(self):
        """
        the identifier name of host

        @rtype: string
        """
        return self._get_field("canonicalName")

    @property
    def position(self):
        """
        the identifier name of host

        @rtype: string
        """
        return self._get_field("position")

    def _show(self, indent = 0):
        print(" "*indent, "Position:", self.position)
        print(" "*indent, "Name:", self.canonical_name)
