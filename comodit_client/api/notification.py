# coding: utf-8
"""
Provides the classes related to notification entity: L{Notification}
and L{NotificationCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper



class NotificationCollection(Collection):
    """
    Collection of notifications. A notification collection is owned by an organization
    L{Organization}.
    """

    def _new(self, json_data = None):
        return Notification(self, json_data)

    def new(self, channel, value = ""):
        """
        Instantiates a new notification object.

        @param channel: The channel is type of notification (Slack, Email,etc ).
        @type name: string
        @param value: value is the json of setting to notify
        @type value: string
        @rtype: L{Notification}
        """

        notification = self._new()
        notification.channel = channel
        notification.value = value
        return notification

    def create(self, channel, value = ""):
        """
        Creates a remote notification entity and returns associated local
        object.

        @param channel: The channel of new notification.
        @type name: string
        @param value: The json value of new notification.
        @type value: string
        @rtype: L{Notification}
        """

        notification = self.new(channel, value)
        notification.create()
        return notification


class Notification(Entity):
    """
    Notification entity representation. Notification is way to notify users from event with origin NOTIFY

    """

    @property
    def organization(self):
        """
        The name of the organization owning this notification.

        @rtype: string
        """

        return self._get_field("organization")
    
    @property
    def name(self):
        """
        The channel of notification.

        @rtype: string
        """

        return self._get_field("channel")
    
    @property
    def value(self):
        """
        The json value of type notification

        @rtype: string
        """

        return self._get_field("value")
    
    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Value:", self.value)
        print(" "*indent, "Organization:", self.organization)
        