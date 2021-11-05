
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity


class OrchestrationHandlerCollection(Collection):
    """
    Collection of orchestration handlers. A orchestration collection is owned by an orchestration
    L{Orchestration}.
    """
    def _new(self, json_data = None):
        return OrchestrationHandler(self, json_data)

    def new(self, json_data):
        """
        Instantiates a new orchestrationHandler object.

        @rtype: L{OrchestrationHandler}
        """

        orchestration_handler = self._new(json_data)
        return orchestration_handler

    def create(self):
        """
        Creates a remote orchestartion_handler entity and returns associated local
        object.

        @rtype: L{OrchestrationHandler}
        """

        orchestration_handler = self.new()
        orchestration_handler.create()
        return orchestration_handler


class OrchestrationHandler(Entity):
    """
    OrchestrationHandler entity representation. Handler is trigger to run orchestration

    """

    @property
    def name(self):
        """
        Resource's name.

        @rtype: string
        """

        return self._get_field("name")

    @name.setter
    def name(self, name):
        """
        Sets resource's name.

        @type name: string
        """

        return self._set_field("name", name)

    @property
    def triggers(self):
        """
        The triggers associated to this handler.

        @rtype: list of string
        """

        return self._get_list_field("triggers")

    @triggers.setter
    def triggers(self, triggers):
        """
        Sets the triggers associated to this handler.

        @param triggers: A list of triggers
        @type triggers: list of string
        """

        self._set_list_field("triggers", triggers)

    def add_trigger(self, trigger):
        """
        Adds a triggers to this handler's list.

        @param trigger: A trigger
        @type trigger: string
        """
        self._add_to_list_field("triggers", trigger)

    def _show(self, indent=0):
        """
        Prints this handler's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Triggers:")
        triggers = self.triggers
        for t in triggers:
            print(" "*(indent + 2), t)