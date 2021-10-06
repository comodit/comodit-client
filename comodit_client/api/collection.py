# coding: utf-8
"""
Provides collections base class (L{Collection}) and related exceptions.
"""
import sys
from builtins import str
from builtins import object
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException

class EntityNotFoundException(PythonApiException):
    """
    Exception raised when an entity was not found in a collection.
    """

    def __init__(self, identifier):
        """
        Creates an instance of EntityNotFoundException.

        @param identifier: The identifier of the entity.
        @type identifier: string
        """
        super(EntityNotFoundException, self).__init__("Entity not found: " + identifier)
        sys.exit("Entity not found: " + identifier)

class Collection(object):
    """
    Collections base class. ComodIT server maintains collections of entities.
    Entities are listed, retrieved, created and deleted through these collections.
    Each collection has a unique URL. An instance of C{Collection} is a local
    representation of a remote ComodIT collection. Requests are sent to
    ComodIT server to L{clear} or L{list} the content of the collection, or to
    L{get} a particular entity of the collection. Creation and update of
    particular remote entities must be handled by subclasses. Also, subclasses
    should provide local entity instantiation helpers. Indeed, creation,
    update and instantiation are specific to entity type.

    Note that some operations on collections are optional. For instance, a
    read-only collection will not allow the deletion, update or creation of
    entities. In particular, most collections do not allow L{clear} operation.

    C{Collection} instances may be iterated with C{for ... in} construction.
    For instance, the following snippet prints the name of all entities of
    collection C{c}.
        >>> for r in c:
        ...    print r.name

    Above snippet is equivalent to:
        >>> for r in c.list():
        ...    print r.name
    """

    def __init__(self, client, url):
        """
        Creates an instance of collection. Note that C{Collection} class should
        never be instantiated directly.

        @param client: ComodIT client.
        @type client: L{Client}
        @param url: URL of remote collection on ComodIT server.
        This URL must be relative to ComodIT server's API URL and should not
        start with a slash.
        @type url: string
        """

        self.url = url
        self.client = client
        self.accept_empty_id = False

    @property
    def _http_client(self):
        """
        HTTP client used by collection instance to interact with ComodIT server.
        """

        return self.client._http_client

    def _handle_error(self, e, identifier):
        if e.code == 404:
            raise EntityNotFoundException(identifier)
        else:
            raise PythonApiException("error " + str(e.code) + ": " + e.message)

    def _create(self, entity, parameters = {}):
        """
        Creates a remote entity given a local representation and updates the
        local representation with newly created remote entity.

        @param entity: Entity's local representation.
        @type entity: L{Entity}
        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings
        """

        try:
            result = self.client._http_client.create(self.url,
                                                   entity.get_json(),
                                                   parameters = parameters)
        except ApiException as e:
            raise PythonApiException("Could not create entity: " + e.message)
        entity.set_json(result)

    def _update(self, entity, parameters = {}):
        """
        Updates a remote entity with a local representation and updates the
        local representation of remote entity.

        @param entity: Entity's local representation.
        @type entity: L{Entity}
        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings

        @raise EntityNotFoundException: If the entity was not found on the
        server.
        """

        entity_id = entity.identifier
        if not entity_id and not self.accept_empty_id:
            raise PythonApiException("Cannot update entity: identifier is empty")

        try:
            result = self.client._http_client.update(self.url + entity_id,
                                                   entity.get_json(),
                                                   parameters = parameters)
        except ApiException as e:
            self._handle_error(e, entity.identifier)
        entity.set_json(result)

    def refresh(self, entity, parameters = {}):
        """
        Updates the local representation of a remote entity.

        @param entity: Entity's local representation.
        @type entity: L{Entity}
        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings

        @raise EntityNotFoundException: If the entity was not found on the
        server.
        """

        try:
            result = self.client._http_client.read(self.url + entity.identifier,
                                                   parameters = parameters)
        except ApiException as e:
            raise PythonApiException("Could not refresh entity: " + e.message)
        entity.set_json(result)

    def list(self, parameters = {}):
        """
        Fetches the entities in this collection.

        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings

        @rtype: list of L{Entity}
        """
        _http_client = self.client._http_client
        try:
            result = _http_client.read(self.url, parameters = parameters)

            entities_list = []
            count = int(result["count"])
            if(count > 0):
                json_list = result["items"]
                for json_res in json_list:
                    entities_list.append(self._new(json_res))

            return entities_list
        except ApiException as e:
            raise PythonApiException("Could not get elements: " + e.message)

    def __iter__(self):
        """
        Provides an iterator on the entities of this collection.

        @return: An iterator object
        @rtype: iterator
        """

        return self.list().__iter__()

    def get(self, identifier = "", parameters = {}):
        """
        Retrieves a particular entity of this collection.

        @param identifier: The identifier of the entity to retrieve.
        @type identifier: string
        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings

        @return: An entity representation.
        @rtype: L{Entity}

        @raise EntityNotFoundException: If the entity was not found on the
        server.
        """

        if not identifier and not self.accept_empty_id:
            raise PythonApiException("Cannot get entity: identifier is empty")

        try:
            result = self.client._http_client.read(self.url + identifier, parameters = parameters)
            return self._new(result)
        except ApiException as e:
            self._handle_error(e, identifier)

    def delete(self, identifier, parameters = {}):
        """
        Deletes a particular entity in this collection.

        @param identifier: The identifier of the entity to delete.
        @type identifier: string
        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings
        """

        if not identifier and not self.accept_empty_id:
            raise PythonApiException("Cannot delete entity: identifier is empty")

        try:
            self.client._http_client.delete(self.url + identifier, parameters = parameters)
        except ApiException as e:
            if e.code != 404:
                self._handle_error(e, identifier)

    def clear(self, parameters = {}):
        """
        Clears the content of the collection i.e. deletes all entities of the
        collection. As a result, a subsequent call to L{list} would return
        an empty list (if nobody re-added entities to the list in the meantime).

        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of strings
        """

        self.client._http_client.delete(self.url, parameters = parameters)
