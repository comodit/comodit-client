# coding: utf-8
"""
Provides the classes related to orchestration context entity: L{OrchestrationContext}
and L{OrchestrationContextCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper

import time


class OrchestrationContextCollection(Collection):
    """
    Collection of orchestration contexts. A orchestration collection is owned by an orchestration
    L{Orchestration}.
    """
    def _new(self, json_data = None):
        return OrchestrationContext(self, json_data)

    def new(self, json_data):
        """
        Instantiates a new orchestrationContext object.

        @rtype: L{OrchestrationContext}
        """

        orchestrationContext = self._new(json_data)
        return orchestrationContext

    def create(self):
        """
        Creates a remote orchestrationContext entity and returns associated local
        object.

        @rtype: L{OrchestrationContext}
        """

        orchestrationContext = self.new()
        orchestrationContext.create()
        return orchestrationContext

class OrchestrationContext(Entity):
    """
    OrchestrationContext entity representation. A orchestration Context is the context of execution of orchestration

    """

    @property
    def identifier(self):
        return str(self._get_field("uuid"))

    @property
    def organization(self):
        """
        The name of the organization owning this orchestration.

        @rtype: string
        """
        return self._get_field("organization")

    @property
    def orchestration(self):
        """
        The name of the orchestration

        @rtype: string
        """
        return self._get_field("orchestration")

    @property
    def orchestration_version(self):
        """
        The version of orchestration.

        @rtype: string
        """
        return self._get_field("orchestrationVersion")

    @property
    def created_by(self):
        """
        The owner who run orchestration

        @rtype: string
        """
        return self._get_field("createdBy")

    @property
    def created(self):
        """
       When orchestration context is created

       @rtype: date
       """
        return self._get_field("created")

    @property
    def started(self):
        """
       When orchestration context is started

       @rtype: date
       """
        return self._get_field("started")

    @property
    def status(self):
        """
       Status of orchestration context. Can't be :
       RUNNING, ERROR, PAUSED, STOPPED

       @rtype: string
       """
        return self._get_field("status")

    @property
    def finished(self):
        """
       When orchestration context is finished

       @rtype: date
       """
        return self._get_field("finished")

    @property
    def host_queues(self):
        """
        List of host's where orchestration is applied.

        @rtype: list of hosts queue L{HostQueue}
        """

        return self._get_list_field("hostQueues", lambda x: HostQueues(x))

    def _show(self, indent = 0):
        print(" "*indent, "organization :", self.organization)
        print(" "*indent, "Orchestration :", self.orchestration)
        print(" "*indent, "id :", self.identifier)
        print(" "*indent, "started:", self.started)
        print(" "*indent, "status:", self.status)
        print(" "*indent, "finished:", self.finished)
        for h in self.host_queues:
            h._show(indent + 2)

    def show_identifier(self):
       print(self.started, "(id: ", self.identifier+")" , self.status)

    def wait_finished(self, time_out = 0, show=False):
        """
       wait current orchestration is finished

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
        Requests to pause orchestration

        @return: Orchestration context
        @rtype: L{OrchestrationContext}
        """
        return self._http_client.update(self.url + "_pause", decode = True)

    def stop(self):
        """
        Requests to stop orchestration

        @return: Orchestration context
        @rtype: L{OrchestrationContext}
        """
        return self._http_client.update(self.url + "_stop", decode = True)

    def restart(self, skip_error = False):
        """
        Requests to restart orchestration in error

        @return: Orchestration context
        @rtype: L{OrchestrationContext}
        """
        parameters = {}
        parameters["skipError"] = skip_error

        return self._http_client.update(self.url + "_restart", parameters, decode = True)

    def resume(self):
        """
        Requests to resume a paused orchestration

        @return: Orchestration context
        @rtype: L{OrchestrationContext}
        """
        return self._http_client.update(self.url + "_resume", decode = True)


class HostQueues(JsonWrapper):

    @property
    def organization(self):
        """
        The organization name

        @rtype: string
        """
        return self._get_field("organization")

    @property
    def environment(self):
        """
        The environment name

        @rtype: string
        """
        return self._get_field("environment")

    @property
    def host(self):
        """
        The host name

        @rtype: string
        """
        return self._get_field("host")

    @property
    def canonical_name(self):
        """
        the identifier name of host

        @rtype: string
        """
        return self._get_field("canonicalName")

    @property
    def position(self):
        """
        position host of execution

        @rtype: string
        """
        return self._get_field("position")

    @property
    def started(self):
        """
        Date when host execution is started

        @rtype: date
        """
        return self._get_field("started")

    @property
    def finished(self):
        """
        Date when host execution is finished

        @rtype: date
        """
        return self._get_field("finished")

    @property
    def status(self):
        """
        Status of execution of host

        @rtype: string
        """
        return self._get_field("status")

    @property
    def error(self):
        """
        Description of error

        @rtype: string
        """
        return self._get_field("error")


    def _show(self, indent = 0):
        print(" "*indent, "Position:", self.position)
        print(" "*indent, "Name:", self.canonical_name)
        print(" "*indent, "Started:", self.started)
        print(" "*indent, "Status:", self.status)
        print(" "*indent, "Finished:", self.finished)
        print(" "*indent, "error:", self.error)

