# coding: utf-8
"""
User collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from user import User

class UserCollection(Collection):
    """
    User collection. Collection of the users available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new UserCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(UserCollection, self).__init__("users", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new User object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{User}
        """

        return User(self._api, json_data)

    def get_uuid(self, username):
        """
        Retrieves the UUID of a user given its name.

        @param username: A user name
        @type username: String
        """
        return self._api.get_directory().get_user_uuid(username)
