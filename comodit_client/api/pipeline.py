# coding: utf-8
"""
Provides the classes related to pipeline entity: L{Pipeline}
and L{PipelineCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.PipelineContext import PipelineContextCollection
from comodit_client.api.hostGroup import OrderedHostGroup
from comodit_client.api.stage import StageCollection



class PipelineCollection(Collection):
    """
    Collection of pipelines. A pipeline collection is owned by an organization
    L{Organization}.
    """
    def _new(self, json_data = None):
        return Pipeline(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new pipeline object.

        @param name: The name of new pipeline.
        @type name: string
        @param description: The description of new pipeline.
        @type description: string
        @rtype: L{pipeline}
        """

        pipeline = self._new()
        pipeline.name = name
        pipeline.description = description
        return pipeline
    
    def create(self, name, description = ""):
        """
        Creates a remote pipeline entity and returns associated local
        object.

        @param name: The name of new pipeline.
        @type name: string
        @param description: The description of new pipeline.
        @type description: string
        @rtype: L{Pipeline}
        """

        pipeline = self.new(name, description)
        pipeline.create()
        return pipeline


class Pipeline(Entity):
    """
    Pipeline entity representation. A pipeline is a sequence of stage and step to execute webhook or orchestration

    """
    @property
    def organization(self):
        """
        The name of the organization owning this pipeline.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def stages(self):
        """
        List of stages ordered by position

        @rtype: list of stages L{Stages}
        """
        return StageCollection(self.client, self.url + "stages/")

    def contexts(self):
        """
        Instantiates the collection of pipelineContext associated to this pipeline.

        @return: The collection of pipeline context associated to this pipeline.
        @rtype: L{PipelineContextCollection}
        """

        return PipelineContextCollection(self.client, self.url + "contexts/")

    def get_context(self, id):
        """
        Fetches a pipeline context of this pipeline given its id.

        @param id: The id of the pipeline context.
        @type id: string
        @rtype: L{PipelineContext}
        """

        return self.contexts().get(id)



    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Organization:", self.organization)
        print(" "*indent, "Stages:")

        #sort by position
        self.stages.sort(key=lambda x: x.order)
        for stages in self.stages:
            stages._show(indent + 2)

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
            result = self._http_client.update(self.url + "_clone", parameters = {"name": clone_name})
            return Orchestration(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone orchestration: " + e.message)

    def run(self):
        """
        Requests to run pipeline

        @return: Pipeline context
        @rtype: L{PipelineContext}
        """
        return self._http_client.update(self.url + "_run", decode = True)

