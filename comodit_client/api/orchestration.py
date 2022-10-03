# coding: utf-8
"""
Provides the classes related to job entity: L{Orchestration}
and L{OrchestrationCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .applicationOperation import ApplicationOperation
from .OrchestrationHandler import OrchestrationHandlerCollection
from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.OrchestrationContext import OrchestrationContextCollection
from comodit_client.api.hostGroup import OrderedHostGroup


class OrchestrationCollection(Collection):
    """
    Collection of orchestrations. A orchestration collection is owned by an organization
    L{Organization}.
    """

    def _new(self, json_data=None):
        return Orchestration(self, json_data)

    def new(self, name, description=""):
        """
        Instantiates a new orchestration object.

        @param name: The name of new orchestration.
        @type name: string
        @param description: The description of new orchestration.
        @type description: string
        @rtype: L{Orchestration}
        """

        orchestration = self._new()
        orchestration.name = name
        orchestration.description = description
        return orchestration

    def create(self, name, description=""):
        """
        Creates a remote orchestration entity and returns associated local
        object.

        @param name: The name of new orchestration.
        @type name: string
        @param description: The description of new orchestration.
        @type description: string
        @rtype: L{Orchestration}
        """

        orchestration = self.new(name, description)
        orchestration.create()
        return orchestration


class Orchestration(Entity):
    """
    Orchestration entity representation. A orchestration is a sequence of service action and handler to execute on host

    """

    @property
    def organization(self):
        """
        The name of the organization owning this orchestration.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def ordered_hostgroups(self):
        """
        List of hostgroups ordered by position

        @rtype: list of ordered_hostgroups L{OrderedHostGroup}
        """

        return self._get_list_field("orderedHostGroup", lambda x: OrderedHostGroup(x))

    @property
    def application_operations(self):
        """
        List of orchestration's applicationOperations.

        @rtype: list of applicationOperations L{ApplicationOperation}
        """

        return self._get_list_field("applicationsOperations", lambda x: ApplicationOperation(x))

    @application_operations.setter
    def application_operations(self, applicationOperations):
        """
        Sets list of orchestration's applicationOperations.

        @param applicationOperations: New list of orchestration's applicationOperations.
        @type applicationOperations: list of ApplicationOperation
        """
        return self._set_list_field("applicationsOperations", applicationOperations)

    def contexts(self):
        """
        Instantiates the collection of orchestrationContext associated to this orchestration.

        @return: The collection of orchestration context associated to this orchestration.
        @rtype: L{OrchestrationContextCollection}
        """

        return OrchestrationContextCollection(self.client, self.url + "contexts/")

    def get_context(self, id):
        """
        Fetches a orchestration context of this orchestration given its id.

        @param name: The id of the orchestration context.
        @type name: string
        @rtype: L{OrchestrationContext}
        """

        return self.contexts().get(id)

    def handlers(self):
        """
        Instantiates the collection of handlers associated to this orchestration.

        @return: The collection of orchestration context associated to this orchestration.
        @rtype: L{OrchestrationHandlerCollection}
        """

        return OrchestrationHandlerCollection(self.client, self.url + "handlers/")

    def _show(self, indent=0):
        print(" " * indent, "Name:", self.name)
        print(" " * indent, "Description:", self.description)
        print(" " * indent, "Organization:", self.organization)
        print(" " * indent, "Actions:")
        for a in self.application_operations:
            a._show(indent + 2)
        print(" " * indent, "Hostgroups:")

        # sort by position
        self.ordered_hostgroups.sort(key=lambda x: x.position)
        for h in self.ordered_hostgroups:
            h._show(indent + 2)

    def show_steps(self, indent=0):
        print(" " * indent, "Name:", self.name)
        print(" " * indent, "Description:", self.description)
        print(" " * indent, "Organization:", self.organization)
        print(" " * indent, "Steps:")
        for a in self.application_operations:
            a._show(indent + 2)

    def clone(self, clone_name):
        """
        Requests the cloning of remote entity. Clone will have given name.
        This name should not already be in use. Note that the hosts in cloned
        orchestration will have a clone with same name in cloned orchestration.
        
        @param clone_name: The name of the clone.
        @type clone_name: string
        @return: The representation of orchestration's clone.
        @rtype: L{Orchestration}
        """

        try:
            result = self._http_client.update(self.url + "_clone", parameters={"name": clone_name})
            return Orchestration(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone orchestration: " + e.message)

    def run(self):
        """
        Requests to run orchestration on hostgroups

        @return: Orchestration context
        @rtype: L{OrchestrationContext}
        """
        return self._http_client.update(self.url + "_run", decode=True)


