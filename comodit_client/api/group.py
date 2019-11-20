
from __future__ import print_function

from .collection import Collection
from .entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.application_key import ApplicationKey

class User(JsonWrapper):
    """
    A ComodIT user's representation.
    """

    @property
    def username(self):
        """
        User's username.

        @rtype: string
        """

        return self._get_field("username")

    @username.setter
    def username(self, username):
        """
        Sets user's username.
        """

        self._set_field("username", username)

    @property
    def full_name(self):
        """
        User's full name.

        @rtype: string
        """
        return self._get_field("fullname")

    @property
    def email(self):
        """
        User's e-mail.

        @rtype: string
        """

        return self._get_field("email")

    def show(self, indent = 0):
        """
        Prints user's representation to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Username:", self.username)
        print(" "*indent, "Full name:", self.full_name)
        print(" "*indent, "E-mail:", self.email)


class GroupCollection(Collection):
    """
    Collection of organization's L{groups<Group>}. Currently, organization, environment or host
    have 5 pre-defined groups:
      - users: Normal users.
      - admin: Administrators, can add/remove users from groups and delete the organization
      - auditors: same right of users but all secrets settings are hidden
      - readonly: Have a read-only access
      - readonly: Have a read-only access
      - no access: Impossible to access the resource
    No group can added or deleted.
    """

    def _new(self, json_data = None):
        return Group(self, json_data)

class GroupOrganizationTreeCollection(Collection):
    """
        Get all GroupCollection on organization and each environment and host where user or applicationKey are defined
    """
    def _new(self, json_data = None):
        return GroupOrganizationTree(self, json_data)

class GroupOrganizationTree(Entity):

    @property
    def organization(self):
        """
        The name of the organization this group is part of.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def groups(self):
        """
        The users and applicationKeys in this group.

        @rtype: list of L{Group}
        """
        return self._get_list_field("groupViews")

    @property
    def environmentGroups(self):
        """
        The users or applicationKeys in environment in this organization.

        @rtype: {GroupEnvironmentTree}
        """
        return self._get_list_field("environmentGroupViews")


    def show(self, indent=0):
        print(" "*(indent + 2), "Organization:", self.organization)

        print(" "*(indent + 2), "Groups:")
        for g in self.groups:
            group = Group(self, json_data=g)
            group._show(indent + 4, lite=True)

        print(" "*(indent + 2), "Environment:")
        for g in self.environmentGroups:
            group = GroupEnvironmentTree(self, json_data=g)
            group.show(indent + 4)

class GroupEnvironmentTreeCollection(Collection):
    """
        Get all GroupCollection on each environments and hosts where user or applicationKey are defined
    """
    def _new(self, json_data = None):
        return GroupEnvironmentTree(self, json_data)


class GroupEnvironmentTree(Entity):
    @property
    def environment(self):
        """
        The name of the environment this group is part of.

        @rtype: string
        """

        return self._get_field("environment")

    @property
    def groups(self):
        """
        The users and applicationKeys in this group.

        @rtype: list of L{User}
        """
        return self._get_list_field("groupViews")

    @property
    def hostGroups(self):
        """
        The users or applicationKeys in hosts of environment in this organization.

        @rtype: {GroupHostTree}
        """
        return self._get_list_field("hostGroupViews")


    def show(self, indent=0):
        print(" "*(indent + 2), "Environment:", self.environment)

        print(" "*(indent + 2), "Groups:")
        for g in self.groups:
            group = Group(self, json_data=g)
            group._show(indent + 4, lite=True)

        print(" "*(indent + 2), "Host:")
        for g in self.hostGroups:
            group = GroupHostTree(self, json_data=g)
            group.show(indent + 4)


class GroupHostTreeCollection(Collection):
    """
        Get all GroupCollection on each hosts where user or applicationKey are defined
    """
    def _new(self, json_data = None):
        return GroupHostTree(self, json_data)



class GroupHostTree(Entity):

    @property
    def host(self):
        """
        The name of the organization this group is part of.

        @rtype: string
        """

        return self._get_field("host")

    @property
    def groups(self):
        """
        The users in this group.

        @rtype: list of L{User}
        """
        return self._get_list_field("groupViews")

    def show(self, indent=0):
        print(" "*(indent + 2), "Host:", self.host)

        print(" "*(indent + 2), "Groups:")
        for g in self.groups:
            group = Group(self, json_data=g)
            group._show(indent + 4, lite=True)


class Group(Entity):
    """
    The representation of an organization's group. A group is defined by a list
    of ComodIT users.
    """

    @property
    def organization(self):
        """
        The name of the organization this group is part of.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def users(self):
        """
        The users in this group.

        @rtype: list of L{User}
        """

        return self._get_list_field("users", lambda x: User(x))

    @property
    def application_keys(self):
        """
        The users in this group.

        @rtype: list of L{User}
        """

        return self._get_list_field("applicationKeys")

    def add_user(self, username):
        """
        Adds a new user to this group. In order to add a user to the group,
        at least its username must be set.

        @param username: The new user's username.
        @type username: string
        """

        user = User()
        user.username = username
        return self._add_to_list_field("users", user)

    def remove_user(self, username):
        """
        Removes given user from list.

        @param username: The username of the user to remove.
        @type username: string
        """

        users = self._get_field("users")  # Field is not interpreted

        i = 0
        for u in users:
            if u["username"] == username:
                break
            i += 1

        if i < len(users):
            del users[i]

    def clear_users(self):
        """
        Remove all users from this group.
        """

        return self._set_list_field("users", [])

    def _show(self, indent = 0, lite=False):
        print(" "*indent, "Name:", self.name)
        if not lite:
            print(" "*indent, "Organization:", self.organization)
            print(" "*indent, "Description:", self.description)

        print(" "*indent, "Users:")
        users = self.users
        for u in users:
            u.show(indent + 2)

        print(" "*indent, "application keys:")
        for a in self.application_keys:
            app = ApplicationKey(self, json_data=a)
            app._show(indent + 4)
