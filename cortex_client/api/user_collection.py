from collection import Collection
from user import User

class UserCollection(Collection):
    def __init__(self, api):
        super(UserCollection, self).__init__("users", api)

    def _new_resource(self, json_data):
        return User(self._api, json_data)

    def get_uuid(self, path):
        return self._api.get_directory().get_user_uuid(path)
