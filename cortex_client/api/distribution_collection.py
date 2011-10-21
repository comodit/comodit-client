from collection import Collection
from distribution import Distribution

class DistributionCollection(Collection):
    def __init__(self, api):
        super(DistributionCollection, self).__init__("distributions", api)

    def _new_resource(self, json_data):
        return Distribution(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_distribution_uuid(path)
