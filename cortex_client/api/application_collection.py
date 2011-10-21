from collection import Collection
from application import Application

class ApplicationCollection(Collection):
    def __init__(self, api):
        super(ApplicationCollection, self).__init__("applications", api)

    def _new_resource(self, json_data):
        return Application(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_application_uuid(path)
