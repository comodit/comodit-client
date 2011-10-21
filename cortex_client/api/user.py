from resource import Resource
from cortex_client.util.json_wrapper import StringFactory

class User(Resource):
    def __init__(self, api = None, json_data = None):
        super(User, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(User, self).set_api(api)
        self._set_collection(api.get_user_collection())

    def get_description(self):
        raise NotImplementedError

    def set_description(self, description):
        raise NotImplementedError

    def get_name(self):
        return self._get_field("username")

    def set_name(self, username):
        return self._set_field("username", username)

    def get_roles(self):
        return self._get_list_field("roles", StringFactory())

    def set_roles(self, roles):
        return self._set_list_field("roles", roles)

    def _show(self, indent = 0):
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "User name:", self.get_name()
        print " "*indent, "Roles:"
        roles = self.get_roles()
        for r in roles:
            print " "*(indent + 2), r

    def dump(self, output_folder):
        raise NotImplementedError

    def load(self, input_folder):
        raise NotImplementedError
