# coding: utf-8
"""
Provides the classes related to job entity: L{OrchestrationContext}
and L{OrchestrationContextCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
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

    def _show(self, indent = 0):
        print(" "*indent, "organization :", self.organization)
        print(" "*indent, "Orchestration :", self.orchestration)
        print(" "*indent, "id :", self.identifier)
        print(" "*indent, "started:", self.started)
        print(" "*indent, "status:", self.status)
        print(" "*indent, "finished:", self.finished)

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
