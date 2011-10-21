from collection import Collection

class HostCollection(Collection):
    def __init__(self, api):
        super(HostCollection, self).__init__("hosts", api)

    def _new_resource(self, json_data):
        from host import Host
        return Host(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_host_uuid_from_path(path)
