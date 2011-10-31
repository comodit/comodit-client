# coding: utf-8
"""
Distribution collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from distribution import Distribution

class DistributionCollection(Collection):
    """
    Distribution collection. Collection of the distributions available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new DistributionCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(DistributionCollection, self).__init__("distributions", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new Distribution object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{Distribution}
        """

        return Distribution(self._api, json_data)

    def get_uuid(self, name):
        """
        Retrieves the UUID of a distribution given its name.

        @param name: The name of a distribution
        @type name: String
        """
        return self._api.get_directory().get_distribution_uuid(name)
