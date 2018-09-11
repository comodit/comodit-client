# coding: utf-8
"""
Provides classes related to notification logs. The following entities have an notification log collection:
  - L{Organization}
  - L{Environment}
  - L{Host}
"""

from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.collection import Collection


class OtherLog(JsonWrapper):
    """
    An Other log. An other log describes actions received by user
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
        A text describing the action.

        @rtype: string
        """

        return self._get_field("message")


class OtherLogCollection(Collection):
    """
    Other logs collection. This is a read-only collection. Also, only
    C{list} operation is implemented.
    """

    def _new(self, json_data = None):
        return OtherLog(json_data)
