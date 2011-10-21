from collection import Collection
from platform import Platform

class PlatformCollection(Collection):
    def __init__(self, api):
        super(PlatformCollection, self).__init__("platforms", api)

    def _new_resource(self, json_data):
        return Platform(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_platform_uuid(path)
