from collection import Collection
from file import File

class FileCollection(Collection):
    def __init__(self, api):
        super(FileCollection, self).__init__("files", api)

    def _new_resource(self, json_data):
        return File(self._api, json_data)

    def get_uuid(self, path):
        return path

    def get_resource(self, uuid):
        result = self._api.get_client().read(self._resource_path + "/"+uuid + "/_meta")
        return self._new_resource(result)