# coding: utf-8
"""
Provides the classes related to step entity: L{Step}
and L{StepCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.OrchestrationContext import OrchestrationContextCollection
from comodit_client.api.hostGroup import OrderedHostGroup



class StepCollection(Collection):
    """
    Collection of steps. A Step collection is owned by a stage
    L{Organization}.
    """
    def _new(self, json_data = None):
        return Step(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new step object.

        @param name: The name of new step.
        @type name: string
        @param description: The description of new step.
        @type description: string
        @rtype: L{step}
        """

        step = self._new()
        step.name = name
        step.description = description
        return step
    
    def create(self, name, description = ""):
        """
        Creates a remote step entity and returns associated local
        object.

        @param name: The name of new step.
        @type name: string
        @param description: The description of new step.
        @type description: string
        @rtype: L{Step}
        """

        step = self.new(name, description)
        step.create()
        return step


class Step(Entity):
    """
    Step entity representation. A step execute webhook or orchestration on hostGroups

    """
    @property
    def stage(self):
        """
        The name of the stage owning this step.

        @rtype: string
        """

        return self._get_field("stage")

    @property
    def order(self):
        """
        the order of stage

        @rtype: integer
        """
        return self._get_field("order")

    @property
    def webhook(self):
        """
        the webhook name to execute

        @rtype: string
        """
        return self._get_field("webhook")

    @property
    def orchestration(self):
        """
        the orchestration name to execute

        @rtype: string
        """
        return self._get_field("orchestration")

    @property
    def ordered_hostgroups(self):
        """
        List of hostgroups ordered by position

        @rtype: list of ordered_hostgroups L{OrderedHostGroup}
        """

        return self._get_list_field("orderedHostGroups", lambda x: OrderedHostGroup(x))

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "order:", self.order)
        print(" "*indent, "webhook:", self.webhook)
        print(" "*indent, "orchestration:", self.orchestration)

        print(" "*indent, "HostGroups:")
        #sort by position
        self.ordered_hostgroups.sort(key=lambda x: x.position)
        for h in self.ordered_hostgroups:
            h._show(indent + 2)

