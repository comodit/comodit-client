# coding: utf-8
"""
Provides the classes related to stage entity: L{Stage}
and L{StageCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.OrchestrationContext import OrchestrationContextCollection
from comodit_client.api.step import StepCollection



class StageCollection(Collection):
    """
    Collection of stage. A stage collection is owned by a pipeline
    L{Organization}.
    """
    def _new(self, json_data = None):
        return Stage(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new stage object.

        @param name: The name of new stage.
        @type name: string
        @param description: The description of new stage.
        @type description: string
        @rtype: L{Stage}
        """

        stage = self._new()
        stage.name = name
        stage.description = description
        return stage
    
    def create(self, name, description = ""):
        """
        Creates a remote stage entity and returns associated local
        object.

        @param name: The name of new stage.
        @type name: string
        @param description: The description of new stage.
        @type description: string
        @rtype: L{Stage}
        """

        stage = self.new(name, description)
        stage.create()
        return stage


class Stage(Entity):
    """
    Stage entity representation. A stage is a sequence of steps

    """
    @property
    def pipeline(self):
        """
        The name of the pipeline owning this stage.

        @rtype: string
        """

        return self._get_field("pipeline")

    @property
    def order(self):
        """
        the order of stage

        @rtype: integer
        """
        return self._get_field("order")

    @property
    def steps(self):
        """
        List of steps ordered

        @rtype: list of steps L{StepCollection}
        """
        return StepCollection(self.client, self.url + "steps/")

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "order:", self.order)
        print(" " * indent, "Steps:")

        # sort by position
        self.steps.sort(key=lambda x: x.order)
        for step in self.steps:
            step._show(indent + 2)



