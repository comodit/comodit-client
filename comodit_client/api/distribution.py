# coding: utf-8
"""
Provides the classes related to distribution entity: L{Distribution}
and L{DistributionCollection}.
"""
from __future__ import print_function

from comodit_client.api.settings import HasSettings
from comodit_client.api.parameters import HasParameters
from comodit_client.api.files import HasFiles
from comodit_client.api.collection import Collection
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.exceptions import PythonApiException
from comodit_client.api.store import IsStoreCapable


class DistributionCollection(Collection):
    """
    Collection of distributions. A distribution collection is owned by an
    L{Organization}.
    """

    def _new(self, json_data = None):
        return Distribution(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new distribution object.

        @param name: The name of new distribution.
        @type name: string
        @param description: The description of new distribution.
        @type description: string
        @rtype: L{Distribution}
        """

        dist = self._new()
        dist.name = name
        dist.description = description
        return dist

    def create(self, name, description = "", flavor_name = None):
        """
        Creates a remote distribution entity and returns associated local
        object. If a flavor name is provided, default settings associated to
        the flavor are also generated.

        @param name: The name of new distribution.
        @type name: string
        @param description: The description of new distribution.
        @type description: string
        @param flavor_name: The flavor name.
        @type flavor_name: string
        @rtype: L{Distribution}
        """

        dist = self.new(name, description)

        if flavor_name != None:
            dist.setup_default_settings(flavor_name)

        dist.create()
        return dist


class Distribution(HasSettings, HasParameters, HasFiles, IsStoreCapable):
    """
    Distribution entity representation. An distribution defines the
    operating system that is installed on a particular host at provisioning
    time. A distribution may have files (kickstart, preseed, userdata, etc.),
    parameters and settings.

    An distribution entity owns 3 collections:
      - settings (L{Setting})
      - parameters (L{Parameter})
      - files (L{File})
    """

    @property
    def organization(self):
        """
        The name of the organization owning this distribution.
        
        @rtype: string
        """

        return self._get_field("organization")

    @property
    def locked(self):
        """
        locked distribution.

        @rtype: bool
        """

        return self._get_field("locked")


    def clone(self, clone_name):
        """
        Requests the cloning of remote entity. Clone will have given name.
        This name should not already be in use.

        @param clone_name: The name of the clone.
        @type clone_name: string
        @return: The representation of distribution's clone.
        @rtype: L{Distribution}
        """

        try:
            result = self._http_client.update(self.url + "_clone", parameters = {"name": clone_name})
            return Distribution(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone distribution: " + e.message)

    def setup_default_settings(self, flavor_name):
        """
        Adds settings defined by given flavor's parameters. Flavor is fetched
        from the server.

        @param flavor_name: The name of the flavor.
        @type flavor_name: string
        """

        if flavor_name != None:
            flavor = self.collection.client.get_flavor(flavor_name)
            for p in flavor.parameters_f:
                self.add_simple_setting(p.key, p.value)

    def _show(self, indent = 0):
        super(Distribution, self)._show(indent)
        print(" " * indent, "Locked:", self.locked)

        self._show_settings(indent)
        self._show_parameters(indent)
        self._show_files(indent)
        self._show_store_fields(indent)


    def lock(self):
        """
        lock distribution.
        """
        try:
            result = self._http_client.create(self.url + "lock", decode = False)
            if result.getcode() != 200:
                raise PythonApiException("Call not accepted by server")
        except ApiException as e:
            raise PythonApiException("Unable to lock distribution : " + e.message)

    def unlock(self):
        """
        unlock distribution
        """
        try:
            result = self._http_client.create(self.url + "unlock", decode = False)
            if result.getcode() != 200:
                raise PythonApiException("Call not accepted by server")
        except ApiException as e:
            raise PythonApiException("Unable to unlock distribution : " + e.message)
