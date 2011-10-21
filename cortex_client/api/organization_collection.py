from collection import Collection
from organization import Organization

class OrganizationCollection(Collection):
    def __init__(self, api):
        super(OrganizationCollection, self).__init__("organizations", api)

    def _new_resource(self, json_data):
        return Organization(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_organization_uuid(path)
