# coding: utf-8
"""
Provides entities base class (L{Entity}).
"""
from __future__ import print_function

import os

from comodit_client.util.json_wrapper import JsonWrapper
import comodit_client.util.path as path

class Entity(JsonWrapper):
    """
    Represents an entity managed by a ComodIT server. An entity instance may
    be used to create or alter a remote entity. In most situations, this
    will imply the update of object's state and then a call to respectively
    L{create} or L{update} in order to 'commit' changes to the server. Note that
    the renaming of an entity is a particular case of update and should be done
    by calling L{rename}. Object's state is generally accessed with properties.

    An entity instance should always be obtained through a collection, either
    by calling L{get<collection.Collection.get>} or a factory method (generally,
    C{new}). This
    ensures that the entity is associated to a collection, which is mandatory
    in order to interact with a ComodIT server. You may instantiate an entity
    without collection, in which case you will still be able to alter object's
    state. However, it will be impossible to commit these changes unless
    L{collection} field is set.
    """

    def __init__(self, collection, json_data = None):
        """
        Creates an instance of entity. Note that C{Entity} class should
        never be instantiated directly.

        @param collection: A collection.
        @type collection: L{Collection}
        @param json_data: A JSON representation of entity's state.
        @type json_data: dict
        """

        super(Entity, self).__init__(json_data)
        self.collection = collection
        self.return_error_code = True

    @property
    def url(self):
        """
        URL of remote entity on ComodIT server.
        This URL is relative to ComodIT server's API URL and should not
        start with a slash.

        @rtype: string
        """

        if self.identifier and self.identifier != "":
            return self.collection.url + self.identifier + "/"
        else:
            return self.collection.url

    def __enforce_connected(self):
        if self.collection is None:
            raise Exception("Entity is not associated to any collection")

    @property
    def _http_client(self):
        """
        HTTP client used to interact with ComodIT server.
        """

        self.__enforce_connected()
        return self.collection._http_client

    @property
    def client(self):
        """
        ComodIT client.

        @rtype: L{Client}
        """

        self.__enforce_connected()
        return self.collection.client

    @property
    def name(self):
        """
        Name of this entity.

        @rtype: string
        """

        return self._get_field("name")

    @name.setter
    def name(self, name):
        """
        Sets the name of this entity.

        @param name: Entity's new name.
        @type name: string
        """

        self._set_field("name", name)

    @property
    def uuid(self):
        """
        ComodIT's UUID for this entity.
        
        @rtype: string
        """

        return self._get_field("uuid")

    @property
    def identifier(self):
        """
        Identifier of the entity. The identifier is unique in entity's
        collection and can therefore be used to get the entity. This value
        is generally entity's name but may also be the UUID or another field
        depending on entity type.

        @rtype: string
        """

        return self.name

    @property
    def label(self):
        """
        A very short description of the entity. This value generally includes
        entity's identifier.

        @rtype: string
        """

        return self.identifier

    @property
    def description(self):
        """
        The description of this entity.

        @rtype: string
        """

        return self._get_field("description")

    @description.setter
    def description(self, description):
        """
        Sets the description of this entity.

        @param description: The new description.
        @type description: string
        """

        self._set_field("description", description)

    def refresh(self, parameters = {}):
        """
        Refreshes the state of this object with data retrieved from ComodIT
        server.
        
        @param parameters: Query parameters to transmit to ComodIT server.
        @type parameters: dict of strings
        
        @raise PythonApiException: If collection is not set.
        """

        self.__enforce_connected()
        self.collection.refresh(self, parameters = parameters)

    def rename(self, new_name):
        """
        Renames remote entity. Note that remote entity will be updated if
        other fields where modified. For example, if you change entity's
        L{description} and then call this method, description of remote
        entity will be updated in addition to its name.
        
        @param new_name: Entity's new name.
        @type new_name: string
        
        @raise PythonApiException: If collection is not set.
        """

        self.__enforce_connected()
        current_url = self.url
        self._set_field("name",new_name)
        self.set_json(self._http_client.update(current_url, self.get_json()))

    def update(self, force = False):
        """
        Updates remote entity with this object's state.

        @param force: Update is forced (optional)
        @type force: bool

        @raise PythonApiException: If collection is not set.
        """
        self.__enforce_connected()
        parameters = {}
        if(force):
            parameters["force"] = "true"
        self.collection._update(self, parameters)

    def create(self, parameters = {}):
        """
        Creates a new entity on the server using this object's state for
        initialization.

        @raise PythonApiException: If collection is not set.
        """

        self.__enforce_connected()
        self.collection._create(self, parameters = parameters)

    def delete(self, parameters = {}):
        """
        Deletes associated remote entity from the server.

        @raise PythonApiException: If collection is not set.
        """

        self.__enforce_connected()
        self.collection.delete(self.identifier, parameters = parameters)

    def show(self, as_json = False, indent = 0):
        """
        Prints this entity's state to standard output. The state may be
        indented. It can also be displayed directly in JSON representation.

        @param as_json: If True, entity's state is displayed in JSON.
        Otherwise, it is displayed in a more user-friendly way.
        @type as_json: bool
        @param indent: The number of spaces to put in front of each displayed
        line (only if as_json is False).
        @type indent: int
        """
        if as_json:
            self.print_json()
        else:
            self._show(indent)

    def _show(self, indent = 0):
        """
        Prints this object's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)

    def dump(self, dest_folder):
        """
        Dumps the state of this object in given folder. Several files may be
        created in destination folder, as well as sub-folders.
        
        @param dest_folder: The path to destination folder
        @type dest_folder: string
        """
        path.ensure(dest_folder)
        plat_file = os.path.join(dest_folder, "definition.json")
        self.dump_json(plat_file)

    def load(self, input_folder):
        """
        Loads the state of this object from files contained by given folder.
        
        @param input_folder: Path to source folder
        @type input_folder: string
        """
        self.load_json(os.path.join(input_folder, "definition.json"))

