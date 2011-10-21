from collection import Collection
from environment import Environment

class EnvironmentCollection(Collection):
    def __init__(self, api):
        super(EnvironmentCollection, self).__init__("environments", api)

    def _new_resource(self, json_data):
        return Environment(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_environment_uuid_from_path(path)
