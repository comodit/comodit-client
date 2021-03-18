# coding: utf-8
"""
Provides the classes related to pipeline context entity: L{PipelineContext}
and L{PipelineContextCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
import sys

import time


class PipelineContextCollection(Collection):
    """
    Collection of pipeline contexts. A pipeline collection is owned by an pipeline
    L{Pipeline}.
    """
    def _new(self, json_data = None):
        return PipelineContext(self, json_data)

    def new(self, json_data):
        """
        Instantiates a new pipelineContext object.

        @rtype: L{PipelineContext}
        """

        context = self._new(json_data)
        return context

    def create(self):
        """
        Creates a remote pipelineContext entity and returns associated local
        object.

        @rtype: L{PipelineContext}
        """

        context = self.new()
        context.create()
        return context

class PipelineContext(Entity):
    """
    PipelineContext entity representation. A pipeline context is the context of execution of pipeline

    """

    @property
    def identifier(self):
        return str(self._get_field("uuid"))

    @property
    def organization(self):
        """
        The name of the organization owning this pipeline.

        @rtype: string
        """
        return self._get_field("organization")

    @property
    def pipeline(self):
        """
        The name of the pipeline

        @rtype: string
        """
        return self._get_field("pipeline")

    @property
    def created_by(self):
        """
        The owner who run pipeline

        @rtype: string
        """
        return self._get_field("createdBy")

    @property
    def created(self):
        """
       When pipeline context is created

       @rtype: date
       """
        return self._get_field("created")

    @property
    def started(self):
        """
       When pipeline context is started

       @rtype: date
       """
        return self._get_field("started")

    @property
    def status(self):
        """
       Status of pipeline context. Can't be :
       RUNNING, ERROR, PAUSED, STOPPED

       @rtype: string
       """
        return self._get_field("status")

    @property
    def finished(self):
        """
       When pipeline context is finished

       @rtype: date
       """
        return self._get_field("finished")

    @property
    def stages(self):
        """
        List of stage context.

        @rtype: list of hosts queue L{StageContext}
        """

        return self._get_list_field("stages", lambda x: StageContexts(x))


    def _show(self, indent = 0):
        print(" "*indent, "Organization :", self.organization)
        print(" "*indent, "Pipeline :", self.pipeline)
        print(" "*indent, "Id :", self.identifier)
        print(" "*indent, "Started:", self.started)
        print(" "*indent, "Status:", self.status)
        print(" "*indent, "Finished:", self.finished)
        print(" "*indent, "Stage:")
        for s in self.stages:
            s._show(indent + 2)

    def show_identifier(self):
       print(self.started, "(id: ", self.identifier+")" , self.status)

    def wait_finished(self, time_out = 0, show=False):
        """
       wait current pipeline is finished

       @rtype: date
       """

        start_time = time.time()

        while self.status == "RUNNING":
            time.sleep(2)
            now = time.time()
            val = int(now - start_time)
            self.refresh()
            if show:
                self._show(4)
            if time_out > 0 and  val > int(time_out):
                sys.exit("timeout")

    def pause(self):
        """
        Requests to pause pipeline

        @return: Pipeline context
        @rtype: L{PipelineContext}
        """
        return self._http_client.update(self.url + "_pause", decode = True)

    def stop(self):
        """
        Requests to stop pipeline

        @return: Pipeline context
        @rtype: L{PipelineContext}
        """
        return self._http_client.update(self.url + "_stop", decode = True)

    def restart(self, skip_error = False):
        """
        Requests to restart pipeline in error

        @return: Pipeline context
        @rtype: L{PipelineContext}
        """
        parameters = {}
        parameters["skipError"] = skip_error

        return self._http_client.update(self.url + "_restart", parameters, decode = True)

    def resume(self):
        """
        Requests to resume a paused pipeline

        @return: Pipeline context
        @rtype: L{PipelineContext}
        """
        return self._http_client.update(self.url + "_resume", decode = True)


class StageContexts(JsonWrapper):

    @property
    def order(self):

        return self._get_field("position")

    @property
    def name(self):
        """
        The stage name

        @rtype: string
        """
        return self._get_field("name")

    @property
    def started(self):
        """
        Date when stage execution is started

        @rtype: date
        """
        return self._get_field("started")

    @property
    def finished(self):
        """
        Date when stage execution is finished

        @rtype: date
        """
        return self._get_field("finished")

    @property
    def status(self):
        """
        Status of execution of stage

        @rtype: string
        """
        return self._get_field("status")

    @property
    def steps(self):
        """
        List of steps context.

        @rtype: list of steps L{StepContext}
        """

        return self._get_list_field("steps", lambda x: StepContexts(x))


    def _show(self, indent=0):
        print(" " * indent, "Order:", self.order)
        print(" " * indent, "Name:", self.name)
        print(" " * indent, "Started:", self.started)
        print(" " * indent, "Status:", self.status)
        print(" " * indent, "Finished:", self.finished)
        print(" " * indent, "Step:")
        for s in self.steps:
            s._show(indent + 2)


class StepContexts(JsonWrapper):

    @property
    def order(self):

        return self._get_field("position")

    @property
    def name(self):
        """
        The step name

        @rtype: string
        """
        return self._get_field("name")

    @property
    def started(self):
        """
        Date when step execution is started

        @rtype: date
        """
        return self._get_field("started")

    @property
    def finished(self):
        """
        Date when step execution is finished

        @rtype: date
        """
        return self._get_field("finished")

    @property
    def status(self):
        """
        Status of execution of step

        @rtype: string
        """
        return self._get_field("status")

    @property
    def webhook(self):
        """
        webhook name executed

        @rtype: string
        """
        return self._get_field("webhook")

    @property
    def orchestration(self):
        """
        orchestration name executed

        @rtype: string
        """
        return self._get_field("orchestration")

    @property
    def orchestration_context(self):
        """
        orchestration context id executed

        @rtype: string
        """
        return self._get_field("orchestrationContext")


    def _show(self, indent=0):
        print(" " * indent, "Order:", self.order)
        print(" " * indent, "Name:", self.name)
        print(" " * indent, "Started:", self.started)
        print(" " * indent, "Status:", self.status)
        print(" " * indent, "Finished:", self.finished)
        print(" " * indent, "Webhook:", self.webhook)
        print(" " * indent, "Orchestration:", self.orchestration)
        print(" " * indent, "Orchestration context:", self.orchestration_context)

