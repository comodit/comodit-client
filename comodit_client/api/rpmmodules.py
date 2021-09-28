from __future__ import print_function
from __future__ import absolute_import

from comodit_client.api.collection import Collection
from comodit_client.api.entity import Entity


class ApplicationRpmModuleCollection(Collection):
    """
    Application rpm module resources collection.
    """

    def _new(self, json_data=None):
        """
        Instantiates a new application rpm module resource object.

        @param json_data: initial state of the object.
        @type json_data: dict
        @return: A new instance of application rpm module resource.
        @rtype: L{RpmModule}
        """

        return RpmModule(self, json_data)


class RpmModule(Entity):
    """
        Application's rpm module resource.
        @see: L{Entity}
    """

    @property
    def stream(self):
        """

        RpmModule's stream name.
        @rtype: string
        """

        return self._get_field("stream")

    @property
    def profile(self):
        """

        RpmModule's profile name.
        @rtype: string
        """

        return self._get_field("profile")

    @property
    def enabled(self):
        """

        RpmModule's enabled
        @rtype: bool
        """

        return self._get_field("enabled")

    def _show(self, indent=0):
        print(" " * indent, self.name + ":")
        print(" " * (indent + 2), "enabled:", self.enabled)
        print(" " * (indent + 2), "stream:", self.stream)
        print(" " * (indent + 2), "profile:", self.profile)
