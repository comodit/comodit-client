# coding: utf-8
"""
Provides classes related to audit logs. The following entities have an audit log collection:
  - L{Organization}
  - L{Environment}
  - L{Host}
"""

from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.collection import Collection


class AuditLog(JsonWrapper):
    """
    An audit log. An audit log describes an operation a ComodIT user executed
    on a particular entity or on an entity it owns (also recursively, via the
    collections it owns). The operation and target entity are described by
    L{message} property.
    """

    @property
    def timestamp(self):
        """
        When the operation was executed. Time has ISO-8601 format.

        @rtype: string
        """

        return self._get_field("timestamp")

    @property
    def message(self):
        """
        A text describing the operation and target entity.

        @rtype: string
        """

        return self._get_field("message")

    @property
    def username(self):
        """
        User's username.

        @rtype: string
        """

        return self._get_field("username")

    @property
    def user_full_name(self):
        """
        User's full name.

        @rtype: string
        """

        return self._get_field("userFullName")


class AuditLogCollection(Collection):
    """
    Audit logs collection. This is a read-only collection. Also, only
    C{list} operation is implemented.
    """

    def _new(self, json_data = None):
        return AuditLog(json_data)
